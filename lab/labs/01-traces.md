# Lab 1: follow one request (ch6, ch7)

**Goal:** see what auto-instrumentation gives you, what you add by hand, and how context crosses service and async boundaries.

1. `make up`, wait a minute, open Jaeger at http://localhost:16686, pick service `storefront`, operation `POST /checkout`, and open a trace.
2. Read the waterfall. You wrote none of the HTTP spans: `FlaskInstrumentor` made the server spans and `RequestsInstrumentor` the client spans (`app/telemetry.py`). The two spans you did write are `load_cart_rows` and `validate_discount` (`app/shop.py`).
3. Click the root span and look at its attributes. `app.user.id`, `app.user.tier`, `app.discount.format` and the rest were set in one call on the server span. That span is the wide event for the request.
4. Now the same thing as rows: `make q F=01_traces`.
   - 1a lists the slowest checkouts.
   - 1b is the waterfall, built with `WHERE TraceId = …  ORDER BY Timestamp`. A trace is a query, not a special data type.
   - 1c shows `send_receipt`. It runs after the response, on a queue, so it is a separate trace. It carries a **link** to the checkout span that caused it.
   - 1d shows the user tier on the `payments` span. `payments` was never sent the tier: it arrived as **baggage**.

**Check yourself**

- Which header carried the trace across services? (`traceparent`: version, trace id, parent span id, flags. See the [W3C spec](https://www.w3.org/TR/trace-context/).)
- Why a link and not a parent for the receipt job? (The parent has finished. A child span would stretch the request's trace and distort its duration.)
- What should never go in baggage? (Secrets and anything large: it is sent on every downstream call.)

**Try:** add an attribute of your own to the checkout span, `docker compose up -d --build storefront`, and group by it in lab 2.
