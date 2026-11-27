"""A three-service shop, instrumented with the real OpenTelemetry SDK.

One file, three roles (SERVICE=storefront | cart | payments), so the whole request path
is readable in one place:

    storefront  POST /checkout
        -> cart      GET  /cart/<user>
        -> payments  POST /charge          (the fault lives here)
        -> receipt job on an in-process queue (async work, joined by a span LINK)

Auto-instrumentation gives the HTTP spans. Everything a debugger would want to slice by
is added by hand to the storefront's server span: one wide event per request (ch5).
"""
import os
import queue
import random
import threading
import time
import uuid

import requests
from flask import Flask, jsonify, request
from opentelemetry import baggage, context, trace
from opentelemetry.trace import Link, Status, StatusCode

import telemetry

SERVICE = os.environ.get("SERVICE", "storefront")
CART_URL = os.environ.get("CART_URL", "http://cart:8080")
PAYMENTS_URL = os.environ.get("PAYMENTS_URL", "http://payments:8080")

app = Flask(SERVICE)
tracer, meter = telemetry.setup(SERVICE, app)

# A metric carries only low-cardinality attributes. The user id stays on the span (ch7, ch31).
checkout_seconds = meter.create_histogram("shop.checkout.duration", unit="s", description="End-to-end checkout time")
fault = {"on": os.environ.get("FAULT", "off") == "on"}
jobs: "queue.Queue[dict]" = queue.Queue()


@app.get("/healthz")
def healthz():
    return "ok"


# ------------------------------------------------------------------ storefront
def discount_format(code: str) -> str:
    return "none" if not code else ("v2" if code.startswith("NEW-") else "v1")


@app.post("/checkout")
def checkout():
    body = request.get_json(force=True)
    started = time.monotonic()
    span = trace.get_current_span()            # the server span Flask auto-instrumentation opened
    user, tier = body["user_id"], body.get("tier", "free")
    code, method = body.get("discount_code", ""), body.get("payment_method", "card")
    # The wide event: business context that makes this request findable later.
    span.set_attributes({
        "app.user.id": user,                               # high cardinality, on purpose
        "app.user.tier": tier,
        "app.cart.items": int(body.get("items", 1)),
        "app.payment.method": method,
        "app.discount.format": discount_format(code),
        "app.client.platform": body.get("platform", "web"),
        "app.build.id": telemetry.BUILD_ID,
        "user.email": body.get("email", ""),                # PII: the Collector hashes this (lab 6)
    })
    # Baggage travels with the trace context, so downstream services can read it without
    # any API change. Keep it small and never put secrets in it.
    token = context.attach(baggage.set_baggage("app.user.tier", tier))
    try:
        cart = requests.get(f"{CART_URL}/cart/{user}", params={"items": body.get("items", 1)}, timeout=5).json()
        pay = requests.post(f"{PAYMENTS_URL}/charge", timeout=5,
                            json={"amount": cart["total"], "method": method, "discount_code": code})
    finally:
        context.detach(token)
    span.set_attribute("app.order.total", cart["total"])
    ok = pay.status_code == 200
    checkout_seconds.record(time.monotonic() - started,
                            {"app.user.tier": tier, "app.payment.method": method, "outcome": "ok" if ok else "error"})
    if not ok:
        span.set_attribute("app.checkout.failure", "payment_declined")
        span.set_status(Status(StatusCode.ERROR, "payment failed"))
        return jsonify(error="payment failed"), 502
    order_id = uuid.uuid4().hex[:12]
    span.set_attribute("app.order.id", order_id)
    # Async follow-up: hand the worker this span's context so it can LINK back to it.
    jobs.put({"order_id": order_id, "link": span.get_span_context()})
    return jsonify(order_id=order_id)


def receipt_worker():
    """Runs later and elsewhere, so it is its own trace. The link says which request caused it (ch6)."""
    while True:
        job = jobs.get()
        with tracer.start_as_current_span("send_receipt", context=context.Context(),   # empty context = new trace
                                          links=[Link(job["link"])],
                                          attributes={"app.order.id": job["order_id"], "messaging.operation.type": "process"}):
            time.sleep(random.uniform(0.005, 0.02))


# ------------------------------------------------------------------------ cart
@app.get("/cart/<user>")
def cart(user):
    items = int(request.args.get("items", 1))
    with tracer.start_as_current_span("load_cart_rows", attributes={"db.system.name": "postgresql", "app.cart.items": items}):
        time.sleep(0.004 + 0.002 * items + random.uniform(0, 0.004))
    return jsonify(user=user, total=round(9.99 * items, 2))


# -------------------------------------------------------------------- payments
@app.post("/charge")
def charge():
    body = request.get_json(force=True)
    span = trace.get_current_span()
    code = body.get("discount_code", "")
    span.set_attributes({"app.payment.method": body["method"], "app.payment.amount": body["amount"],
                         "app.discount.format": discount_format(code),
                         "app.user.tier": baggage.get_baggage("app.user.tier") or "unknown"})   # arrived via baggage
    time.sleep(random.uniform(0.015, 0.045))
    if code:
        with tracer.start_as_current_span("validate_discount") as v:
            v.set_attribute("app.discount.format", discount_format(code))
            # The injected fault: the new code format hits a slow path and sometimes fails.
            if fault["on"] and code.startswith("NEW-"):
                time.sleep(random.uniform(0.6, 1.1))
                if random.random() < 0.3:
                    err = TimeoutError("discount service timed out")
                    v.record_exception(err)
                    v.set_status(Status(StatusCode.ERROR, str(err)))
                    span.set_status(Status(StatusCode.ERROR, "discount validation failed"))
                    return jsonify(error="discount validation failed"), 500
            else:
                time.sleep(random.uniform(0.002, 0.006))
    return jsonify(status="charged")


@app.post("/admin/fault")
def admin_fault():
    fault["on"] = bool(request.get_json(force=True).get("on"))
    trace.get_current_span().set_attribute("app.fault.on", fault["on"])
    return jsonify(fault=fault["on"])


if SERVICE == "storefront":
    threading.Thread(target=receipt_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), threaded=True)
