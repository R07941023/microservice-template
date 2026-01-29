# Claude Code Guidelines

## Project Structure

This is a microservice template project with:
- `frontend/`: Next.js React application
- `backend/`: Python FastAPI microservices
- `deployment/`: Kubernetes configurations
- `docker-compose.yml`: Local development environment

## General Rules

- Always read existing code before making modifications
- Prefer editing existing files over creating new ones
- Follow existing patterns in the codebase
- Run linters before committing

## Python Code Standards (Backend)

### Docstrings (Required)

Every module, class, and function MUST have a docstring.

```python
"""Module description."""

class MyClass:
    """Class description."""

    def my_method(self, arg: str) -> bool:
        """
        Method description.

        Args:
            arg: Argument description.

        Returns:
            Return value description.

        Raises:
            ValueError: When something is wrong.
        """
        pass
```

### Exception Handling (Specific Exceptions)

NEVER catch broad `Exception`. Always use specific exception types.

```python
# CORRECT - Specific exceptions
from minio.error import S3Error
from redis.exceptions import RedisError

try:
    minio_client.get_object(bucket, key)
except S3Error as e:
    logger.error("MinIO error: %s", e)

try:
    await redis_client.get(key)
except RedisError as e:
    logger.error("Redis error: %s", e)

# WRONG - Too broad
try:
    minio_client.get_object(bucket, key)
except Exception as e:  # Pylint W0718: broad-exception-caught
    logger.error("Error: %s", e)
```

Common specific exceptions:
- MinIO: `minio.error.S3Error`
- Redis: `redis.exceptions.RedisError`
- HTTP client: `httpx.HTTPStatusError`, `httpx.RequestError`
- JSON: `json.JSONDecodeError`
- Network: `ConnectionError`, `TimeoutError`

When re-raising a different exception, use `from e` to preserve the chain:

```python
# CORRECT - Preserve exception chain
except S3Error as e:
    logger.error("MinIO error: %s", e)
    raise HTTPException(status_code=404, detail="Not found") from e

# WRONG - Loses original traceback (Pylint W0707)
except S3Error as e:
    raise HTTPException(status_code=404, detail="Not found")
```

### Resource Management (Close Connections)

Always close resources that require cleanup. Use `try/finally` to ensure cleanup.

#### MinIO Response

`minio.get_object()` returns a `urllib3.HTTPResponse` that MUST be closed:

```python
# CORRECT - Always close MinIO response
response = None
try:
    response = minio_client.get_object(bucket, object_name)
    data = response.read()
    return data
except S3Error as e:
    logger.error("MinIO error: %s", e)
    raise
finally:
    if response:
        response.close()
        response.release_conn()

# WRONG - Connection leak!
response = minio_client.get_object(bucket, object_name)
data = response.read()
# response never closed - connections will leak
```

#### Redis (Async)

Use `CacheClient` from utils which handles connection pooling automatically.
Close on shutdown via `lifespan`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.connect()
    yield
    await cache.close()  # Always close on shutdown
```

### Logging (Lazy % Formatting)

ALWAYS use lazy % formatting in logging. NEVER use f-strings.

```python
# CORRECT
logger.info("Connected to %s:%s", host, port)
logger.error("Failed to process %s: %s", item, error)
logger.debug("User %s performed action %s", user_id, action)

# WRONG - Do NOT use f-strings
logger.info(f"Connected to {host}:{port}")
logger.error(f"Failed to process {item}: {error}")
```

### Import Order

Follow this order with blank lines between groups:

```python
"""Module docstring."""

# 1. Standard library
import asyncio
import logging
import os
from contextlib import asynccontextmanager

# 2. Third-party packages
from fastapi import FastAPI, HTTPException
from minio import Minio

# 3. Local imports
from models import MyModel
from services.my_service import my_function
from utils.cache import CacheClient
```

### Type Hints

Always use type hints for function arguments and return values.

```python
async def get_item(item_id: str, include_meta: bool = False) -> dict:
    """Get item by ID."""
    pass

def process_items(items: list[str]) -> list[dict]:
    """Process multiple items."""
    pass
```

### FastAPI Patterns

#### Health Check Endpoints

Use two separate endpoints for Kubernetes probes:

```python
from utils.health import router as health_router

app = FastAPI(lifespan=lifespan)
app.include_router(health_router)  # Provides /health/live

@app.get("/health/ready")
async def readiness() -> dict:
    """Readiness probe - check dependencies."""
    # Check your service's dependencies (DB, cache, etc.)
    pass
```

#### Background Tasks for Non-Blocking Operations

Use `BackgroundTasks` for operations that shouldn't block the response:

```python
@app.get("/items/{item_id}")
async def get_item(item_id: str, background_tasks: BackgroundTasks) -> Response:
    """Get item with background caching."""
    data = await fetch_data(item_id)

    # Cache in background - don't block response
    background_tasks.add_task(cache.set, item_id, data)

    return data
```

#### Lifespan for Startup/Shutdown

Use `lifespan` context manager for resource management:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    await cache.connect()
    yield
    # Shutdown
    await cache.close()

app = FastAPI(lifespan=lifespan)
```

### Shared Utilities

Place reusable code in `backend/utils/`:

- `auth.py`: JWT and authentication utilities
- `cache.py`: Redis cache client
- `health.py`: Common health check router

Import in services:

```python
from utils.cache import CacheClient
from utils.health import router as health_router
from utils.auth import decode_jwt_from_header
```

## TypeScript/JavaScript Code Standards (Frontend)

### Use TypeScript

Always use TypeScript (`.ts`, `.tsx`) instead of JavaScript.

### Component Structure

```typescript
interface Props {
  title: string;
  onClick: () => void;
}

export function MyComponent({ title, onClick }: Props) {
  return <button onClick={onClick}>{title}</button>;
}
```

## Kubernetes Deployment

### Health Probes

Always configure both probes in deployment.yaml:

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

## Git Commit Messages

Use conventional commits:

```
feat(backend): add Redis caching to image retriever
fix(frontend): resolve auth redirect loop
refactor(utils): extract common cache client
docs: update API documentation
```
