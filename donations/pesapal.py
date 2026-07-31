"""
Pesapal API 3.0 client.

Flow implemented here:
  1. get_access_token()        -> POST /api/Auth/RequestToken
  2. get_or_register_ipn_id()  -> GET /api/URLSetup/GetIpnList (reuse if found)
                                   POST /api/URLSetup/RegisterIPN (otherwise)
  3. submit_order_request()    -> POST /api/Transactions/SubmitOrderRequest
  4. get_transaction_status()  -> GET /api/Transactions/GetTransactionStatus

Reference: https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json
"""
import requests
from django.conf import settings


class PesapalError(Exception):
    """Raised whenever Pesapal rejects a request or a network call fails."""
    pass


def _base_url():
    return settings.PESAPAL_BASE_URL


def _check_credentials():
    if not settings.PESAPAL_CONSUMER_KEY or not settings.PESAPAL_CONSUMER_SECRET:
        raise PesapalError(
            "Pesapal is not configured: PESAPAL_CONSUMER_KEY / "
            "PESAPAL_CONSUMER_SECRET are missing."
        )


def get_access_token():
    """Returns a bearer token string, valid for ~5 minutes."""
    _check_credentials()
    url = f"{_base_url()}/api/Auth/RequestToken"
    payload = {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
    }
    try:
        resp = requests.post(url, json=payload, headers={"Accept": "application/json"}, timeout=15)
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise PesapalError(f"Could not reach Pesapal (auth): {exc}") from exc

    token = data.get("token")
    if not token:
        raise PesapalError(data.get("message") or "Pesapal authentication failed.")
    return token


def get_or_register_ipn_id(token, ipn_url, notification_type="GET"):
    """Reuses an already-registered IPN URL if one matches, otherwise registers a new one."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        resp = requests.get(f"{_base_url()}/api/URLSetup/GetIpnList", headers=headers, timeout=15)
        existing = resp.json()
        if isinstance(existing, list):
            for entry in existing:
                if entry.get("url") == ipn_url:
                    return entry.get("ipn_id")
    except (requests.RequestException, ValueError):
        pass  # fall through and try to register a fresh one

    try:
        resp = requests.post(
            f"{_base_url()}/api/URLSetup/RegisterIPN",
            json={"url": ipn_url, "ipn_notification_type": notification_type},
            headers=headers,
            timeout=15,
        )
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise PesapalError(f"Could not reach Pesapal (IPN registration): {exc}") from exc

    ipn_id = data.get("ipn_id")
    if not ipn_id:
        raise PesapalError(data.get("message") or "Could not register IPN URL with Pesapal.")
    return ipn_id


def submit_order_request(token, *, merchant_reference, amount, description, callback_url,
                          ipn_id, email, first_name, last_name, phone_number=""):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "id": merchant_reference,
        "currency": settings.PESAPAL_CURRENCY,
        "amount": float(amount),
        "description": description[:100] if description else "Donation",
        "callback_url": callback_url,
        "notification_id": ipn_id,
        "billing_address": {
            "email_address": email or "",
            "phone_number": phone_number or "",
            "country_code": "UG",
            "first_name": first_name or "Donor",
            "middle_name": "",
            "last_name": last_name or "",
            "line_1": "",
            "line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "zip_code": "",
        },
    }
    try:
        resp = requests.post(
            f"{_base_url()}/api/Transactions/SubmitOrderRequest",
            json=payload, headers=headers, timeout=20,
        )
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise PesapalError(f"Could not reach Pesapal (submit order): {exc}") from exc

    redirect_url = data.get("redirect_url")
    order_tracking_id = data.get("order_tracking_id")
    if not redirect_url or not order_tracking_id:
        error = data.get("error") or {}
        raise PesapalError(error.get("message") or data.get("message") or "Pesapal could not create this order.")

    return {
        "order_tracking_id": order_tracking_id,
        "redirect_url": redirect_url,
        "merchant_reference": data.get("merchant_reference", merchant_reference),
    }


def get_transaction_status(token, order_tracking_id):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    try:
        resp = requests.get(
            f"{_base_url()}/api/Transactions/GetTransactionStatus",
            params={"orderTrackingId": order_tracking_id},
            headers=headers, timeout=15,
        )
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise PesapalError(f"Could not reach Pesapal (status check): {exc}") from exc
