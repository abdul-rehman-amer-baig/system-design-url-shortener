# Known Drawbacks & Future Improvements

---

## 1. Write-Service is a Single Point of Failure

Only one `write-service` instance is running. If it goes down, no URLs can be created.

**Fix:** Run multiple write-service instances behind nginx. The Redis `INCR` counter is atomic so it's safe to share across multiple writers — no duplicate short codes will be generated.

---

## 2. Cache Stampede

If Redis goes down and restarts empty, all 3 read replicas will get cache misses simultaneously and hammer PostgreSQL with the same queries at once. At scale this can take the DB down entirely.

**Fix:** Implement mutex locking — only one replica fetches from DB for a given key at a time, the others wait for the result. Libraries like `redis-py-lock` handle this.

---

## 3. nginx is a Single Point of Failure

Read replicas are horizontally scaled, but nginx itself has no redundancy. If nginx crashes, the entire system goes down regardless of how many healthy replicas exist.

**Fix:** In production, run multiple nginx instances behind a cloud load balancer (AWS ALB, Cloudflare, etc.) which handles failover automatically.

---

## 4. No Authentication

Anyone can hit `POST /urls` and create short URLs. The `user_id` field exists in the DB but nothing enforces that the requester actually owns that user. There is no token validation anywhere.

**Fix:** Add JWT middleware to the write-service. Requests without a valid token should be rejected with `401 Unauthorized` before reaching any business logic.
