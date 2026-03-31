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

---

## 5. Short Codes are Predictable

Sqids generates codes based on an incrementing Redis counter (`1 → abc`, `2 → abd`, etc.). Someone could enumerate all URLs in the system by simply incrementing the short code.

**Fix:** Configure a random salt in Sqids so the output is not sequential, or switch to UUIDs for short code generation.

---

## 6. Alembic Migrations are Not Automated

Alembic is set up in the write-service but migrations do not run automatically when containers start. This means a fresh deployment requires manual intervention to set up the DB schema.

**Fix:** Add an `entrypoint.sh` to the write-service that runs `alembic upgrade head` before starting uvicorn:

```bash
#!/bin/bash
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then update the Dockerfile:
```dockerfile
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
```
