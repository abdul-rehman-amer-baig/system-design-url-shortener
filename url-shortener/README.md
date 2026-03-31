# URL Shortener

A production-style URL shortener built with a microservices architecture — separated read and write paths, Redis caching, and nginx as an API gateway.

---

## Architecture

```
Client
  |
  v :80
nginx (API Gateway)
  |
  |--- POST /urls, POST /users ---------> write-service:8000
  |--- GET  /urls/{code} (round-robin) -> read-service-1:8001
                                          read-service-2:8001
                                          read-service-3:8001
                                               |
                                        [Redis cache]
                                               |
                                        [PostgreSQL]
```

### Services

| Service | Role | Port |
|---|---|---|
| nginx | API Gateway — single public entry point | 80 |
| write-service | Creates users and short URLs | 8000 (internal) |
| read-service (x3) | Resolves short URLs, serves from cache | 8001 (internal) |
| PostgreSQL | Persistent storage | 5432 (internal), 5434 (host dev only) |
| Redis | URL cache + atomic short code counter | 6379 (internal) |

---

## API Endpoints

All requests go through `http://localhost` (nginx on port 80).

### Users

| Method | Path | Description |
|---|---|---|
| `POST` | `/users` | Create a user |

### URLs

| Method | Path | Description |
|---|---|---|
| `POST` | `/urls` | Create a short URL |
| `GET` | `/urls/{short_code}` | Resolve a short URL |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health/write` | Write-service liveness |
| `GET` | `/health/read` | Read-service liveness (shows which replica served it) |

### Swagger UI

| Service | URL |
|---|---|
| Write-service | http://localhost/docs |
| Read-service | http://localhost/read/docs |

---

## Running Locally

**Start everything:**
```bash
docker compose up --build
```

---

## How It Works

### Creating a short URL
1. write-service calls `INCR` on a Redis counter to get a unique integer
2. That integer is encoded into a short alphanumeric code via [Sqids](https://sqids.org)
3. The URL record is written to PostgreSQL

### Resolving a short URL
1. read-service checks Redis cache first — if found, returns immediately
2. On a cache miss, queries PostgreSQL and stores the result in Redis with a TTL
3. Subsequent requests for the same code are served entirely from cache

### Custom aliases
- If a custom alias is requested and it's already taken by an **active** URL, returns `409 Conflict`
- If the alias exists but has **expired**, it is automatically reclaimed and reassigned

### Expiration
- URLs with an `expiration_time` in the past are rejected at creation (`422`)
- Expired URLs return `410 Gone` and are evicted from Redis cache on access

---

## Redis Configuration

```yaml
redis-server --maxmemory 100mb --maxmemory-policy allkeys-lfu
```

- **100mb** memory cap
- **LFU eviction** — least frequently used keys are evicted when memory is full, keeping popular URLs cached longer

---

## TODO

- [ ] Build a front-end
- [ ] Deploy to Render
- [ ] Link live URL in portfolio
