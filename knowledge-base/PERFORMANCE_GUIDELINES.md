# KellerAI Performance Guidelines
# Version: 1.0
# Last Updated: 2025-10-14

## Performance Checklist

### API Performance

- [ ] API response time < 200ms for 95th percentile
- [ ] Database queries optimized (indexes, no N+1)
- [ ] Caching implemented for frequently accessed data
- [ ] Pagination for large result sets
- [ ] Compression enabled (gzip/brotli)
- [ ] CDN for static assets
- [ ] Connection pooling configured
- [ ] Appropriate timeout values set

### Database Performance

- [ ] Indexes on foreign keys and frequently queried columns
- [ ] Query execution plans reviewed
- [ ] Batch operations instead of loops
- [ ] Database connection pooling
- [ ] Read replicas for read-heavy workloads
- [ ] Archival strategy for old data
- [ ] Slow query logging enabled
- [ ] Regular VACUUM/ANALYZE (PostgreSQL)

### Frontend Performance

- [ ] Bundle size < 500KB (gzipped)
- [ ] Code splitting implemented
- [ ] Lazy loading for routes and components
- [ ] Image optimization (WebP, compression)
- [ ] Fonts optimized (subset, preload)
- [ ] Critical CSS inlined
- [ ] Service worker for caching
- [ ] Lighthouse score > 90

### ML Model Performance

- [ ] Model inference time < 500ms
- [ ] Batch inference for multiple requests
- [ ] Model quantization applied
- [ ] GPU utilization optimized
- [ ] Model caching enabled
- [ ] Async inference for non-blocking
- [ ] Model versioning for A/B testing

## Performance Benchmarks

### API Response Times

| Endpoint Type | Target (p50) | Target (p95) | Target (p99) |
|---------------|--------------|--------------|--------------|
| Simple GET    | < 50ms       | < 100ms      | < 200ms      |
| Complex GET   | < 100ms      | < 200ms      | < 500ms      |
| POST/PUT      | < 100ms      | < 250ms      | < 500ms      |
| Heavy POST    | < 200ms      | < 500ms      | < 1000ms     |

### Database Query Times

| Query Type           | Target (p95) |
|----------------------|--------------|
| Primary key lookup   | < 1ms        |
| Indexed query        | < 10ms       |
| Join query (2 tables)| < 20ms       |
| Complex query        | < 100ms      |
| Aggregation          | < 200ms      |

### Frontend Metrics

| Metric                    | Target    |
|---------------------------|-----------|
| First Contentful Paint    | < 1.5s    |
| Largest Contentful Paint  | < 2.5s    |
| Time to Interactive       | < 3.5s    |
| Cumulative Layout Shift   | < 0.1     |
| First Input Delay         | < 100ms   |

## Database Optimization

### Indexing Strategy

```sql
-- ✅ Index foreign keys
CREATE INDEX idx_posts_author_id ON posts(author_id);

-- ✅ Index frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- ✅ Composite index for common query patterns
CREATE INDEX idx_posts_author_published ON posts(author_id, published, created_at DESC);

-- ✅ Partial index for filtered queries
CREATE INDEX idx_active_users ON users(email) WHERE deleted_at IS NULL;

-- ✅ Index for text search
CREATE INDEX idx_posts_title_gin ON posts USING gin(to_tsvector('english', title));
```

### Query Optimization

```typescript
// ❌ BAD - N+1 query problem
const users = await prisma.user.findMany();
for (const user of users) {
  user.posts = await prisma.post.findMany({
    where: { authorId: user.id }
  });
}

// ✅ GOOD - Single query with include
const users = await prisma.user.findMany({
  include: {
    posts: {
      select: {
        id: true,
        title: true,
        createdAt: true,
      },
      where: { published: true },
      orderBy: { createdAt: 'desc' },
      take: 10,
    },
  },
});

// ✅ GOOD - Select only needed fields
const users = await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    email: true,
    // Don't fetch large fields like passwordHash if not needed
  },
});
```

### Connection Pooling

```typescript
// Prisma connection pool configuration
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // Connection pool settings
  connection_limit: 20,
  pool_timeout: 30,
});

// PostgreSQL connection pool with pg
const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20, // Maximum pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

## Caching Strategies

### Redis Caching

```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

// Cache-aside pattern
async function getCachedUser(userId: string): Promise<User> {
  const cacheKey = `user:${userId}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // Cache miss - fetch from database
  const user = await prisma.user.findUnique({
    where: { id: userId },
  });

  if (user) {
    // Store in cache with TTL
    await redis.setex(cacheKey, 3600, JSON.stringify(user)); // 1 hour
  }

  return user;
}

// Cache invalidation
async function updateUser(userId: string, data: UpdateUserInput): Promise<User> {
  const user = await prisma.user.update({
    where: { id: userId },
    data,
  });

  // Invalidate cache
  await redis.del(`user:${userId}`);

  return user;
}
```

### HTTP Caching

```typescript
// Cache-Control headers
app.get('/api/users/:id', async (req, res) => {
  const user = await userService.getUser(req.params.id);

  // Cache for 5 minutes
  res.setHeader('Cache-Control', 'public, max-age=300');
  res.json(user);
});

// ETag support
app.get('/api/users/:id', async (req, res) => {
  const user = await userService.getUser(req.params.id);
  const etag = generateEtag(user);

  if (req.headers['if-none-match'] === etag) {
    return res.status(304).end(); // Not modified
  }

  res.setHeader('ETag', etag);
  res.json(user);
});
```

## Frontend Performance

### Code Splitting

```typescript
// Route-based code splitting
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Router>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

// Component-based code splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart data={data} />
      </Suspense>
    </div>
  );
}
```

### Image Optimization

```typescript
// Next.js Image component (automatic optimization)
import Image from 'next/image';

function UserAvatar({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={200}
      height={200}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
      quality={85}
      formats={['webp', 'avif']}
    />
  );
}

// Manual optimization with modern formats
function OptimizedImage({ src, alt }: { src: string; alt: string }) {
  return (
    <picture>
      <source srcSet={`${src}.avif`} type="image/avif" />
      <source srcSet={`${src}.webp`} type="image/webp" />
      <img src={`${src}.jpg`} alt={alt} loading="lazy" />
    </picture>
  );
}
```

### React Performance

```typescript
// Memoization
import { memo, useMemo, useCallback } from 'react';

const UserCard = memo(({ user }: { user: User }) => {
  return <div>{user.name}</div>;
});

function UserList({ users }: { users: User[] }) {
  // Memoize expensive computations
  const sortedUsers = useMemo(() => {
    return users.sort((a, b) => a.name.localeCompare(b.name));
  }, [users]);

  // Memoize callbacks
  const handleUserClick = useCallback((userId: string) => {
    console.log('User clicked:', userId);
  }, []);

  return (
    <div>
      {sortedUsers.map(user => (
        <UserCard
          key={user.id}
          user={user}
          onClick={() => handleUserClick(user.id)}
        />
      ))}
    </div>
  );
}
```

## ML Model Optimization

### Model Quantization

```python
import torch

# Load full precision model
model = torch.load('model.pth')

# Quantize to INT8
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Save quantized model (typically 4x smaller)
torch.save(quantized_model, 'model_quantized.pth')
```

### Batch Inference

```python
# ❌ BAD - Process one at a time
for document in documents:
    result = model.predict(document)
    results.append(result)

# ✅ GOOD - Batch processing
batch_size = 32
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    batch_results = model.predict_batch(batch)
    results.extend(batch_results)
```

### Model Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str) -> np.ndarray:
    """Cache embeddings for frequently queried text."""
    return embedding_model.encode(text)

# Or use Redis for distributed caching
async def get_cached_embedding(text: str) -> np.ndarray:
    cache_key = f"embedding:{hash(text)}"
    cached = await redis.get(cache_key)

    if cached:
        return np.frombuffer(cached)

    embedding = embedding_model.encode(text)
    await redis.setex(cache_key, 3600, embedding.tobytes())

    return embedding
```

## Monitoring and Profiling

### Performance Monitoring

```typescript
// API response time tracking
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;

    // Send to monitoring service
    metrics.timing('api.response_time', duration, {
      method: req.method,
      route: req.route?.path,
      status: res.statusCode,
    });

    // Log slow requests
    if (duration > 1000) {
      logger.warn('Slow request', {
        method: req.method,
        path: req.path,
        duration,
      });
    }
  });

  next();
});
```

### Database Query Profiling

```typescript
// Prisma query logging
const prisma = new PrismaClient({
  log: [
    {
      emit: 'event',
      level: 'query',
    },
  ],
});

prisma.$on('query', (e) => {
  if (e.duration > 100) {
    logger.warn('Slow query', {
      query: e.query,
      params: e.params,
      duration: e.duration,
    });
  }
});
```

## Performance Testing

### Load Testing with k6

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% error rate
  },
};

export default function () {
  const res = http.get('https://api.kellerai.com/v1/users');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

### Database Performance Testing

```bash
# Run pgbench for PostgreSQL performance testing
pgbench -i -s 50 mydb  # Initialize with scale factor 50
pgbench -c 10 -j 2 -t 1000 mydb  # 10 clients, 2 threads, 1000 transactions
```

---

**Version**: 1.0
**Last Updated**: 2025-10-14
**Review Frequency**: Quarterly
**Owner**: Platform Team
