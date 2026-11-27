# Lab 2: wide events and high cardinality (ch1, ch5)

**Goal:** feel the difference between "any attribute is a GROUP BY" and "only the labels someone planned for".

`make q F=02_wide_events`

- **2a** counts distinct values per attribute. `app.user.id` has hundreds; `app.user.tier` has 3. A metrics system charges you per distinct label combination, so user id cannot be a label. Here it is just a column value.
- **2b** answers a question nobody planned: latency by tier × payment method × platform.
- **2c** finds the individual users who had the worst time.
- **2d** shows the average of per-group averages next to the true average. In my run the first was 213 ms and the second 87 ms. Once you aggregate at write time, you cannot get the second number back.

Now open Prometheus (http://localhost:9090) and try to answer 2c with `shop_calls_total`. You can't: the user id was never a label, and adding it would create one series per user.

**Check yourself**

- Define cardinality and dimensionality. (Distinct values of one field; number of fields per event.)
- Why does the book call pre-aggregation a one-way trip?
- When is a metric still the right tool? (Cheap, long-retention trends and alerts on a known question: see lab 4.)

**Try:** `make sql`, then write a query for "P95 by build id and discount format". With one build it is dull; change `BUILD_ID` for `payments` in `docker-compose.yaml`, restart it, and compare builds.
