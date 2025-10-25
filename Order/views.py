# Order/views.py
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


HEADERS = {
    "Authorization": f"SECRET_KEY {settings.KAKAO_PAY_KEY}",
    "Content-Type": "application/json",
}

@csrf_exempt
@require_http_methods(["POST"])
def payment_detail_api(request):
    """
    POST /api/order/detail/
    { "tid": "T1234567890" } 형태로 요청하면
    KakaoPay 주문 조회 결과 중 주요 정보만 반환
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    tid = (payload.get("tid") or "").strip()
    if not tid:
        return HttpResponseBadRequest("Missing 'tid'")

    url = "https://open-api.kakaopay.com/online/v1/payment/order"
    body = {"cid": settings.KAKAO_PAY_CID, "tid": tid}

    try:
        res = requests.post(url, json=body, headers=HEADERS, timeout=10)
    except requests.RequestException as e:
        return HttpResponse(f"KakaoPay request error: {e}", status=502)

    if res.status_code != 200:
        return HttpResponse(res.text, status=res.status_code)

    data = res.json()

    amount_total = (data.get("amount") or {}).get("total")
    method_type = data.get("payment_method_type")
    item_name = data.get("item_name")
    approved_at = data.get("approved_at")

    approved_at = data.get("approved_at")
    if not approved_at:
        for act in (data.get("payment_action_details") or []):
            if act.get("payment_action_type") == "PAYMENT" and act.get("approved_at"):
                approved_at = act["approved_at"]
                break

    return JsonResponse({
        "tid": tid,
        "item_name": item_name,
        "amount": amount_total,
        "payment_method_type": method_type,
        "approved_at": approved_at,
        "raw": data,
    })
