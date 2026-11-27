# Lab 3: find the culprit without a hypothesis (ch8)

**Goal:** debug from first principles. No dashboard for this failure exists, and you are not allowed to guess.

1. `make fault-on`, wait two minutes.
2. In Grafana (http://localhost:3000, dashboard *Checkout*) P95 climbs. That tells you *that* something is wrong, not *what*.
3. `make q F=03_bubbleup`. The query takes the bad requests (errors or slower than 500 ms), compares each attribute value's share in that set with its share in the rest, and sorts by the gap. In my run the top row was:

   | attribute | value | share_of_bad | share_of_good | gap |
   |---|---|---|---|---|
   | app.discount.format | v2 | 1.0 | 0.033 | 0.967 |

   Every bad request used the new discount-code format; 3% of good ones did.
4. Confirm it: in Jaeger, search `storefront` with tag `app.discount.format=v2`, open a slow trace, and the time is in `payments › validate_discount`. A failed one has an `exception` event with the error type.
5. `make fault-off`.

This is the core analysis loop: start from the symptom, slice by every dimension, follow the biggest difference, repeat. The query automates the middle step. Honeycomb's BubbleUp does this in the UI; here it is 20 lines of SQL over wide events.

**Check yourself**

- Why did rows 3 and 4 (`app.cart.items = 3`) show a gap too? (Small sample noise. The gap for the real cause is an order of magnitude larger. Always check the counts.)
- What would this look like with only the three pillars? (A latency graph, error logs without the discount format, and a trace if it happened to be sampled.)

**Try:** change the fault in `app/shop.py` to depend on two attributes (say, v2 codes *and* `gift_card`). Does the query still surface it? What would you add?
