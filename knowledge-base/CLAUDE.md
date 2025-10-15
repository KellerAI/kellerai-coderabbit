# KellerAI Development Standards and Architectural Guidelines
# CLAUDE.md - Comprehensive Development Reference
# Version: 1.0
# Last Updated: 2025-10-14

---

## Table of Contents

1. [Introduction and Purpose](#introduction-and-purpose)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack](#technology-stack)
4. [System Design Principles](#system-design-principles)
5. [API Design Guidelines](#api-design-guidelines)
6. [Data Modeling Conventions](#data-modeling-conventions)
7. [Security Best Practices](#security-best-practices)
8. [Performance Optimization](#performance-optimization)
9. [Testing Requirements](#testing-requirements)
10. [Documentation Standards](#documentation-standards)
11. [Code Review Process](#code-review-process)
12. [Deployment and DevOps](#deployment-and-devops)

---

## Introduction and Purpose

This document serves as the comprehensive development reference for KellerAI engineering teams. It establishes coding standards, architectural patterns, and best practices for building scalable, secure, and maintainable AI/ML applications.

### Document Scope

- **Primary Audience**: Software engineers, AI/ML engineers, DevOps engineers
- **Application**: All KellerAI projects including web applications, APIs, ML pipelines, and data processing systems
- **Authority**: This document supersedes informal coding practices and serves as the source of truth for development standards

### How to Use This Document

1. **For New Projects**: Review the entire document before starting development
2. **For Code Reviews**: Reference specific sections when providing feedback
3. **For Onboarding**: Use as a training resource for new team members
4. **For Updates**: Propose changes through the standard RFC process

---

## Architecture Overview

### High-Level System Architecture

KellerAI applications follow a **layered microservices architecture** with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (React Web Apps, Mobile Apps, CLI Tools, Third-party APIs) │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/WSS
┌────────────────────┼────────────────────────────────────────┐
│                API Gateway & Load Balancer                   │
│          (Rate Limiting, Authentication, Routing)            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │             │
┌───────▼──────┐  ┌──▼─────────┐ ┌▼──────────────┐
│  REST APIs   │  │  GraphQL   │ │  WebSocket    │
│  (FastAPI/   │  │  Server    │ │  Server       │
│  Express)    │  │            │ │               │
└───────┬──────┘  └──┬─────────┘ └┬──────────────┘
        │            │              │
┌───────┴────────────┴──────────────┴──────────────┐
│           Business Logic Layer                    │
│  (Services, Controllers, Domain Logic)            │
└───────┬────────────┬──────────────┬───────────────┘
        │            │              │
┌───────▼──────┐  ┌──▼─────────┐ ┌─▼──────────────┐
│  Data Access │  │  ML Models │ │  Message Queue │
│  Layer       │  │  & Inference│ │  (Bull/Redis)  │
│  (Prisma/    │  │  (PyTorch/ │ │                │
│  TypeORM)    │  │  TensorFlow)│ │                │
└───────┬──────┘  └──┬─────────┘ └─┬──────────────┘
        │            │              │
┌───────▼────────────▼──────────────▼───────────────┐
│              Data Storage Layer                    │
│  (PostgreSQL, MongoDB, Redis, S3, Vector DBs)     │
└────────────────────────────────────────────────────┘
```

### Architectural Principles

#### 1. Separation of Concerns

Each layer has a well-defined responsibility:

- **Presentation Layer**: User interface and API endpoints
- **Business Logic Layer**: Core application logic and workflows
- **Data Access Layer**: Database operations and external data sources
- **Infrastructure Layer**: Cross-cutting concerns (logging, monitoring, caching)

```typescript
// ✅ GOOD - Clear separation
// presentation/controllers/user.controller.ts
export class UserController {
  constructor(private userService: UserService) {}

  async createUser(req: Request, res: Response) {
    const user = await this.userService.createUser(req.body);
    res.json(successResponse(user));
  }
}

// business/services/user.service.ts
export class UserService {
  constructor(private userRepository: UserRepository) {}

  async createUser(data: CreateUserInput): Promise<User> {
    this.validateUserData(data);
    return this.userRepository.create(data);
  }
}

// data/repositories/user.repository.ts
export class UserRepository {
  async create(data: CreateUserInput): Promise<User> {
    return prisma.user.create({ data });
  }
}
```

#### 2. Domain-Driven Design (DDD)

Organize code around business domains rather than technical layers:

```
src/
├── domains/
│   ├── users/
│   │   ├── user.entity.ts
│   │   ├── user.service.ts
│   │   ├── user.repository.ts
│   │   ├── user.controller.ts
│   │   ├── dtos/
│   │   └── tests/
│   ├── documents/
│   │   ├── document.entity.ts
│   │   ├── document.service.ts
│   │   ├── document-processor.ts
│   │   └── ml-models/
│   └── billing/
│       ├── billing.entity.ts
│       ├── billing.service.ts
│       ├── payment-gateway.ts
│       └── subscription-manager.ts
├── shared/
│   ├── interfaces/
│   ├── utils/
│   ├── middlewares/
│   └── decorators/
└── infrastructure/
    ├── database/
    ├── cache/
    ├── queue/
    └── storage/
```

#### 3. Dependency Injection

Use dependency injection for loose coupling and testability:

```typescript
// ✅ GOOD - Constructor injection
export class DocumentService {
  constructor(
    private documentRepository: DocumentRepository,
    private mlModelService: MLModelService,
    private storageService: StorageService,
    private logger: Logger
  ) {}

  async processDocument(file: File): Promise<ProcessedDocument> {
    this.logger.info(`Processing document: ${file.name}`);

    const storedFile = await this.storageService.upload(file);
    const extracted = await this.mlModelService.extractData(storedFile);
    const document = await this.documentRepository.create(extracted);

    return document;
  }
}

// ❌ BAD - Hard dependencies
export class DocumentService {
  async processDocument(file: File) {
    // Hard-coded dependencies - difficult to test
    const storage = new S3Storage();
    const model = new BertModel();
    const db = new PostgresDB();
  }
}
```

#### 4. CQRS (Command Query Responsibility Segregation)

Separate read and write operations for complex domains:

```typescript
// Commands (writes)
export class CreateUserCommand {
  constructor(public readonly data: CreateUserInput) {}
}

export class CreateUserHandler {
  async execute(command: CreateUserCommand): Promise<User> {
    const user = await this.userRepository.create(command.data);
    await this.eventBus.publish(new UserCreatedEvent(user));
    return user;
  }
}

// Queries (reads)
export class GetUserQuery {
  constructor(public readonly userId: string) {}
}

export class GetUserHandler {
  async execute(query: GetUserQuery): Promise<UserDTO> {
    // Can use read-optimized database or cache
    return this.userReadRepository.findById(query.userId);
  }
}
```

---

## Technology Stack

### Backend Technologies

#### Primary Languages
- **Python 3.10+**: AI/ML workloads, data processing, scientific computing
- **TypeScript/Node.js 18+**: API services, real-time applications, tooling

#### Web Frameworks
- **FastAPI** (Python): High-performance async APIs, automatic OpenAPI docs
- **Express.js** (TypeScript): Flexible web framework for Node.js APIs
- **NestJS** (TypeScript): Enterprise-grade framework with built-in DI

#### Databases
- **PostgreSQL 15+**: Primary relational database for structured data
- **MongoDB 6+**: Document store for flexible schemas and analytics
- **Redis 7+**: Caching, session storage, message broker
- **Qdrant/Pinecone**: Vector databases for embeddings and semantic search

#### ML/AI Stack
- **PyTorch 2.0+**: Deep learning models and research
- **TensorFlow 2.x**: Production ML models
- **Hugging Face Transformers**: Pre-trained NLP models
- **LangChain**: LLM application framework
- **scikit-learn**: Classical ML algorithms

### Frontend Technologies

#### Primary Framework
- **React 18+**: Component-based UI library with hooks
- **TypeScript**: Type-safe JavaScript superset
- **Next.js 14+**: React framework with SSR/SSG capabilities

#### State Management
- **Zustand**: Lightweight state management
- **React Query (TanStack Query)**: Server state management
- **React Hook Form**: Form state and validation

#### UI/Styling
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Re-usable component library
- **Radix UI**: Unstyled, accessible components

### DevOps and Infrastructure

- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **GitHub Actions**: CI/CD pipelines
- **AWS/GCP**: Cloud infrastructure
- **Terraform**: Infrastructure as Code
- **Datadog/New Relic**: Monitoring and observability

---

## System Design Principles

### 1. SOLID Principles

#### Single Responsibility Principle (SRP)
Each class/module should have one reason to change.

```python
# ✅ GOOD - Single responsibility
class EmailSender:
    """Responsible only for sending emails."""
    def send(self, to: str, subject: str, body: str) -> None:
        # Email sending logic
        pass

class UserNotifier:
    """Responsible for user notification logic."""
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def notify_user_created(self, user: User) -> None:
        self.email_sender.send(
            to=user.email,
            subject="Welcome!",
            body=self._build_welcome_message(user)
        )

# ❌ BAD - Multiple responsibilities
class UserService:
    def create_user(self, data: dict) -> User:
        # Validation
        self.validate_email(data['email'])
        # Database operation
        user = self.db.insert(data)
        # Email sending
        self.smtp.send_email(user.email, "Welcome!")
        # Logging
        self.log_to_file(f"User created: {user.id}")
        return user
```

#### Open/Closed Principle (OCP)
Software entities should be open for extension but closed for modification.

```typescript
// ✅ GOOD - Extensible through interfaces
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
}

class StripeProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // Stripe-specific implementation
  }
}

class PayPalProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // PayPal-specific implementation
  }
}

class PaymentService {
  constructor(private processor: PaymentProcessor) {}

  async charge(amount: number): Promise<PaymentResult> {
    return this.processor.process(amount);
  }
}

// Adding new payment method doesn't modify existing code
class CryptoProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // Crypto-specific implementation
  }
}
```

#### Dependency Inversion Principle (DIP)
Depend on abstractions, not concretions.

```python
# ✅ GOOD - Depend on abstraction
from abc import ABC, abstractmethod

class DocumentStorage(ABC):
    """Abstract storage interface."""
    @abstractmethod
    async def save(self, document: bytes, path: str) -> str:
        pass

class S3Storage(DocumentStorage):
    async def save(self, document: bytes, path: str) -> str:
        # S3-specific implementation
        pass

class DocumentProcessor:
    def __init__(self, storage: DocumentStorage):
        self.storage = storage  # Depends on abstraction

    async def process(self, doc: bytes) -> str:
        # Processing logic
        return await self.storage.save(doc, "processed/")

# ❌ BAD - Depend on concrete implementation
class DocumentProcessor:
    def __init__(self):
        self.storage = S3Storage()  # Tightly coupled to S3
```

### 2. Twelve-Factor App Methodology

#### Config (Factor III)
Store configuration in environment variables, never in code.

```typescript
// ✅ GOOD - Environment-based configuration
import { z } from 'zod';

const ConfigSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  API_PORT: z.string().transform(Number).default('3000'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

export const config = ConfigSchema.parse(process.env);

// ❌ BAD - Hardcoded configuration
const config = {
  database: 'postgresql://localhost:5432/mydb',
  jwtSecret: 'my-secret-key',
  port: 3000,
};
```

#### Backing Services (Factor IV)
Treat databases, caches, and queues as attached resources.

```python
# ✅ GOOD - Connection via environment
from sqlalchemy import create_engine
from redis import Redis

database = create_engine(os.environ['DATABASE_URL'])
cache = Redis.from_url(os.environ['REDIS_URL'])
```

#### Logs (Factor XI)
Treat logs as event streams, never write to files directly.

```typescript
// ✅ GOOD - Structured logging to stdout
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

logger.info('User created', { userId: '123', email: 'user@example.com' });

// ❌ BAD - Writing to file
fs.appendFileSync('app.log', `User created: ${userId}\n`);
```

### 3. Microservices Patterns

#### API Gateway Pattern
Single entry point for all client requests.

```typescript
// api-gateway/src/index.ts
import { createProxyMiddleware } from 'http-proxy-middleware';

app.use('/api/users', authenticate, createProxyMiddleware({
  target: 'http://user-service:3001',
  changeOrigin: true,
}));

app.use('/api/documents', authenticate, createProxyMiddleware({
  target: 'http://document-service:3002',
  changeOrigin: true,
}));
```

#### Circuit Breaker Pattern
Prevent cascading failures in distributed systems.

```typescript
import CircuitBreaker from 'opossum';

const options = {
  timeout: 3000, // Request timeout
  errorThresholdPercentage: 50, // Open circuit at 50% error rate
  resetTimeout: 30000, // Try to close after 30s
};

const breaker = new CircuitBreaker(callExternalService, options);

breaker.on('open', () => logger.warn('Circuit breaker opened'));
breaker.on('halfOpen', () => logger.info('Circuit breaker half-open'));
breaker.on('close', () => logger.info('Circuit breaker closed'));

// Usage
try {
  const result = await breaker.fire(requestData);
} catch (error) {
  // Circuit is open or request failed
  return fallbackResponse;
}
```

---

## API Design Guidelines

### REST API Conventions

#### Resource Naming
- Use plural nouns for collections: `/api/users`, `/api/documents`
- Use hierarchical paths for relationships: `/api/users/{userId}/posts`
- Use kebab-case for multi-word resources: `/api/payment-methods`

```
✅ GOOD REST API Design:
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/{id}      # Get user
PUT    /api/v1/users/{id}      # Update user (full)
PATCH  /api/v1/users/{id}      # Update user (partial)
DELETE /api/v1/users/{id}      # Delete user

GET    /api/v1/users/{userId}/posts        # User's posts
POST   /api/v1/users/{userId}/posts        # Create post for user
GET    /api/v1/users/{userId}/posts/{id}   # Get specific post

❌ BAD REST API Design:
GET    /api/v1/getUsers           # Verb in URL
POST   /api/v1/user/create        # Verb in URL
GET    /api/v1/users/123/delete   # Delete via GET
POST   /api/v1/updateUser         # No resource identification
```

#### HTTP Methods and Status Codes

**GET Requests**:
- `200 OK`: Successful retrieval
- `404 Not Found`: Resource doesn't exist
- `400 Bad Request`: Invalid query parameters

**POST Requests**:
- `201 Created`: Resource created successfully (include `Location` header)
- `400 Bad Request`: Invalid request body
- `409 Conflict`: Resource already exists

**PUT/PATCH Requests**:
- `200 OK`: Update successful
- `204 No Content`: Update successful with no response body
- `404 Not Found`: Resource doesn't exist

**DELETE Requests**:
- `204 No Content`: Deletion successful
- `404 Not Found`: Resource doesn't exist

#### Response Format
```typescript
// Success response
interface SuccessResponse<T> {
  success: true;
  data: T;
  metadata?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
}

// Error response
interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
    documentation?: string;
  };
}

// Example responses
{
  "success": true,
  "data": {
    "id": "user-123",
    "name": "Alice",
    "email": "alice@example.com"
  },
  "metadata": {
    "timestamp": "2025-10-14T12:00:00Z",
    "requestId": "req-abc-123",
    "version": "v1"
  }
}

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    },
    "documentation": "https://docs.kellerai.com/errors/validation"
  }
}
```

### API Versioning

Use URL versioning for clarity:

```
https://api.kellerai.com/v1/users
https://api.kellerai.com/v2/users  # Breaking changes
```

### GraphQL API Standards

```typescript
// schema.graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts(first: Int, after: String): PostConnection!
  createdAt: DateTime!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type Query {
  user(id: ID!): User
  users(first: Int, after: String, filter: UserFilter): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): UserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
}

# Resolver implementation
export const resolvers = {
  Query: {
    user: async (_: any, { id }: { id: string }, context: Context) => {
      return context.dataloaders.userLoader.load(id);
    },
  },
  Mutation: {
    createUser: async (_: any, { input }: { input: CreateUserInput }, context: Context) => {
      const user = await context.services.userService.create(input);
      return { user };
    },
  },
  User: {
    posts: async (user: User, args: PaginationArgs, context: Context) => {
      return context.dataloaders.userPostsLoader.load({
        userId: user.id,
        ...args,
      });
    },
  },
};
```

---

## Data Modeling Conventions

### Database Schema Design

#### Naming Conventions
- **Tables**: Plural snake_case (`users`, `payment_methods`)
- **Columns**: snake_case (`created_at`, `user_id`)
- **Primary Keys**: `id` (UUID or auto-incrementing integer)
- **Foreign Keys**: `{table}_id` (`user_id`, `document_id`)
- **Timestamps**: `created_at`, `updated_at`, `deleted_at`

#### Schema Example (Prisma)
```prisma
model User {
  id            String    @id @default(uuid())
  email         String    @unique
  name          String
  passwordHash  String    @map("password_hash")
  role          UserRole  @default(USER)

  posts         Post[]
  comments      Comment[]

  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")
  deletedAt     DateTime? @map("deleted_at")

  @@index([email])
  @@index([createdAt])
  @@map("users")
}

model Post {
  id          String    @id @default(uuid())
  title       String
  content     String    @db.Text
  published   Boolean   @default(false)

  authorId    String    @map("author_id")
  author      User      @relation(fields: [authorId], references: [id], onDelete: Cascade)

  comments    Comment[]
  tags        Tag[]

  createdAt   DateTime  @default(now()) @map("created_at")
  updatedAt   DateTime  @updatedAt @map("updated_at")
  publishedAt DateTime? @map("published_at")

  @@index([authorId])
  @@index([published, publishedAt])
  @@map("posts")
}

enum UserRole {
  ADMIN
  USER
  GUEST
}
```

### Data Integrity

#### Referential Integrity
```sql
-- ✅ GOOD - Foreign key constraints
CREATE TABLE posts (
  id UUID PRIMARY KEY,
  author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for foreign keys
CREATE INDEX idx_posts_author_id ON posts(author_id);
```

#### Data Validation
```typescript
// ✅ GOOD - Schema validation at database layer
const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  age: z.number().int().min(18).max(120),
});

// ✅ GOOD - Database check constraints (Prisma)
model User {
  age Int @check(age >= 18 AND age <= 120)
}
```

---

## Security Best Practices

### Authentication

#### JWT Implementation
```typescript
import jwt from 'jsonwebtoken';

interface JwtPayload {
  userId: string;
  email: string;
  role: string;
}

export function generateAccessToken(payload: JwtPayload): string {
  return jwt.sign(payload, process.env.JWT_SECRET!, {
    expiresIn: '15m', // Short-lived access tokens
    issuer: 'kellerai',
    audience: 'api',
  });
}

export function generateRefreshToken(userId: string): string {
  return jwt.sign({ userId }, process.env.REFRESH_TOKEN_SECRET!, {
    expiresIn: '7d',
    issuer: 'kellerai',
  });
}

export function verifyToken(token: string): JwtPayload {
  try {
    return jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload;
  } catch (error) {
    throw new UnauthorizedError('Invalid token');
  }
}
```

### Authorization

#### Role-Based Access Control (RBAC)
```typescript
enum Permission {
  USER_READ = 'user:read',
  USER_WRITE = 'user:write',
  USER_DELETE = 'user:delete',
  ADMIN_ACCESS = 'admin:access',
}

const RolePermissions: Record<UserRole, Permission[]> = {
  ADMIN: [Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE, Permission.ADMIN_ACCESS],
  USER: [Permission.USER_READ, Permission.USER_WRITE],
  GUEST: [Permission.USER_READ],
};

function hasPermission(user: User, permission: Permission): boolean {
  const permissions = RolePermissions[user.role];
  return permissions.includes(permission);
}

// Middleware
function requirePermission(permission: Permission) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !hasPermission(req.user, permission)) {
      throw new ForbiddenError('Insufficient permissions');
    }
    next();
  };
}
```

### Input Validation and Sanitization

#### XSS Prevention
```typescript
import DOMPurify from 'isomorphic-dompurify';

function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: [],
  });
}
```

#### SQL Injection Prevention
Always use parameterized queries (Prisma/TypeORM handle this automatically).

```typescript
// ✅ GOOD - Parameterized query
await prisma.user.findMany({
  where: {
    email: userEmail, // Automatically parameterized
  },
});

// ❌ BAD - String interpolation
await prisma.$queryRaw`SELECT * FROM users WHERE email = '${userEmail}'`;
```

### Secrets Management

```typescript
// ✅ GOOD - Environment variables
const config = {
  database: process.env.DATABASE_URL!,
  jwtSecret: process.env.JWT_SECRET!,
  apiKey: process.env.OPENAI_API_KEY!,
};

// ❌ BAD - Hardcoded secrets
const config = {
  database: 'postgresql://user:pass@localhost/db',
  jwtSecret: 'my-secret-key',
};
```

---

## Performance Optimization

### Database Query Optimization

#### N+1 Query Problem
```typescript
// ❌ BAD - N+1 queries
const users = await prisma.user.findMany();
for (const user of users) {
  user.posts = await prisma.post.findMany({
    where: { authorId: user.id },
  });
}

// ✅ GOOD - Single query with include
const users = await prisma.user.findMany({
  include: {
    posts: true,
  },
});
```

#### Indexing Strategy
```sql
-- Index commonly queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- Composite index for common query patterns
CREATE INDEX idx_posts_author_published ON posts(author_id, published, created_at DESC);
```

### Caching Strategies

#### Redis Caching
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

async function getCachedUser(userId: string): Promise<User | null> {
  const cached = await redis.get(`user:${userId}`);
  if (cached) {
    return JSON.parse(cached);
  }

  const user = await prisma.user.findUnique({ where: { id: userId } });
  if (user) {
    await redis.setex(`user:${userId}`, 3600, JSON.stringify(user)); // 1 hour TTL
  }

  return user;
}
```

### API Response Optimization

#### Pagination
Always paginate large datasets.

```typescript
interface PaginationParams {
  page: number;
  limit: number;
}

async function getPaginatedUsers(params: PaginationParams) {
  const offset = (params.page - 1) * params.limit;

  const [items, totalItems] = await Promise.all([
    prisma.user.findMany({
      skip: offset,
      take: params.limit,
    }),
    prisma.user.count(),
  ]);

  return {
    items,
    pagination: {
      currentPage: params.page,
      totalPages: Math.ceil(totalItems / params.limit),
      totalItems,
    },
  };
}
```

---

## Testing Requirements

### Test Coverage Targets

- **Overall Coverage**: Minimum 80%
- **Critical Paths**: 100% (authentication, payments, data validation)
- **Business Logic**: >90%
- **API Endpoints**: >85%

### Testing Pyramid

```
         /\
        /E2E\        10% - End-to-End Tests
       /______\
      /        \
     /Integration\ 30% - Integration Tests
    /____________\
   /              \
  /  Unit Tests    \ 60% - Unit Tests
 /__________________\
```

### Unit Testing Examples

```typescript
// user.service.test.ts
describe('UserService', () => {
  let userService: UserService;
  let userRepository: MockRepository<User>;

  beforeEach(() => {
    userRepository = createMockRepository();
    userService = new UserService(userRepository);
  });

  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Arrange
      const input = {
        name: 'Alice',
        email: 'alice@example.com',
        age: 30,
      };
      const expectedUser = { id: '1', ...input };
      userRepository.create.mockResolvedValue(expectedUser);

      // Act
      const result = await userService.createUser(input);

      // Assert
      expect(result).toEqual(expectedUser);
      expect(userRepository.create).toHaveBeenCalledWith(input);
    });

    it('should throw ValidationError for invalid email', async () => {
      // Arrange
      const input = {
        name: 'Bob',
        email: 'invalid-email',
        age: 25,
      };

      // Act & Assert
      await expect(userService.createUser(input)).rejects.toThrow(ValidationError);
    });
  });
});
```

---

## Documentation Standards

### Code Documentation

#### Function Documentation (JSDoc/Docstrings)
```typescript
/**
 * Processes a document and extracts structured data using ML models.
 *
 * This function handles the complete document processing pipeline including
 * file validation, text extraction, ML inference, and data storage.
 *
 * @param documentPath - Path to the document file
 * @param options - Processing configuration options
 * @param options.useOcr - Enable OCR for scanned documents
 * @param options.modelVersion - ML model version to use
 * @returns Processed document with extracted data
 * @throws {ValidationError} If document format is invalid
 * @throws {ProcessingError} If ML inference fails
 *
 * @example
 * ```typescript
 * const result = await processDocument('/path/to/doc.pdf', {
 *   useOcr: true,
 *   modelVersion: 'v2.1'
 * });
 * ```
 */
async function processDocument(
  documentPath: string,
  options: ProcessingOptions = {}
): Promise<ProcessedDocument> {
  // Implementation
}
```

### API Documentation

Use OpenAPI/Swagger for REST APIs:

```typescript
/**
 * @openapi
 * /api/v1/users:
 *   post:
 *     summary: Create a new user
 *     tags: [Users]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateUserInput'
 *     responses:
 *       201:
 *         description: User created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 *       400:
 *         description: Invalid input
 *       409:
 *         description: Email already exists
 */
app.post('/api/v1/users', createUserHandler);
```

---

## Code Review Process

### Pre-Review Checklist

Before requesting code review, ensure:

- [ ] All tests pass locally
- [ ] Code coverage meets minimum requirements (>80%)
- [ ] Linter passes with no errors
- [ ] Security scan passes (no critical vulnerabilities)
- [ ] Documentation updated (README, API docs, code comments)
- [ ] Breaking changes documented
- [ ] Database migrations tested
- [ ] Performance impact assessed

### Review Guidelines

**Reviewers should check for**:

1. **Correctness**: Does the code do what it's supposed to do?
2. **Security**: Are there any security vulnerabilities?
3. **Performance**: Are there any performance issues?
4. **Maintainability**: Is the code easy to understand and modify?
5. **Testing**: Are there adequate tests?
6. **Documentation**: Is the code properly documented?

---

## Deployment and DevOps

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run test:coverage
      - run: npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ./deploy.sh production
```

### Monitoring and Observability

Implement comprehensive monitoring:

- **Application Metrics**: Response times, error rates, throughput
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Business Metrics**: User signups, API usage, revenue
- **Logs**: Structured logging with correlation IDs
- **Alerts**: Automated alerts for critical issues

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Maintained By**: KellerAI Platform Team
**For Questions**: Contact platform@kellerai.com
