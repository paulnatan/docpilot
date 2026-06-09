import os
from fastapi import APIRouter, HTTPException, Header, Request

try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
from pydantic import BaseModel
from jose import jwt
from db.supabase import get_client

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://readygen-app.netlify.app")

PLANS = {
    "pro": {
        "price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""),
        "name": "Pro",
        "amount": 1900,  # €19.00 in centesimi
    },
    "team": {
        "price_id": os.getenv("STRIPE_TEAM_PRICE_ID", ""),
        "name": "Team",
        "amount": 4900,  # €49.00 in centesimi
    },
}


def _get_user_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "dev_secret"), algorithms=["HS256"])
        user_id = payload["sub"]
        result = get_client().table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return result.data[0]
    except Exception:
        raise HTTPException(status_code=401, detail="Token non valido")


class CheckoutRequest(BaseModel):
    plan: str  # "pro" | "team"


@router.post("/create-checkout")
async def create_checkout(request: CheckoutRequest, authorization: str = Header(...)):
    """Crea una sessione Stripe Checkout e restituisce l'URL di pagamento."""
    token = authorization.replace("Bearer ", "")
    user = _get_user_from_token(token)

    plan = PLANS.get(request.plan)
    if not plan:
        raise HTTPException(status_code=400, detail="Piano non valido")

    if not STRIPE_AVAILABLE or not os.getenv("STRIPE_SECRET_KEY"):
        raise HTTPException(status_code=503, detail="Stripe non configurato")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "paypal", "sepa_debit"],
            mode="subscription",
            customer_email=user.get("email", ""),
            line_items=[{
                "price": plan["price_id"],
                "quantity": 1,
            }],
            metadata={
                "user_id": str(user["id"]),
                "plan": request.plan,
            },
            success_url=f"{FRONTEND_URL}/dashboard.html?payment=success&plan={request.plan}",
            cancel_url=f"{FRONTEND_URL}/dashboard.html?payment=cancelled",
        )
        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Riceve eventi Stripe (payment_intent.succeeded, ecc.) e aggiorna il piano utente."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            import json
            event = json.loads(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        plan = session.get("metadata", {}).get("plan")

        if user_id and plan:
            get_client().table("users").update({
                "plan": plan,
                "stripe_customer_id": session.get("customer"),
                "stripe_subscription_id": session.get("subscription"),
            }).eq("id", user_id).execute()

    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        if customer_id:
            get_client().table("users").update({"plan": "free"}).eq(
                "stripe_customer_id", customer_id
            ).execute()

    return {"received": True}


@router.get("/status")
async def payment_status(authorization: str = Header(...)):
    """Restituisce il piano corrente dell'utente."""
    token = authorization.replace("Bearer ", "")
    user = _get_user_from_token(token)
    return {
        "plan": user.get("plan", "free"),
        "stripe_customer_id": user.get("stripe_customer_id"),
    }
