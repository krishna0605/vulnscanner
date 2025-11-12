# Architecture Documentation

## System Overview

The Enhanced Vulnerability Scanner is designed as a modern, scalable web application following microservices architecture principles. The system is built to handle high-throughput web crawling operations while maintaining security, reliability, and performance.

## Architecture Principles

### 1. Separation of Concerns
- **Frontend**: User interface and experience
- **Backend API**: Business logic and data management
- **Crawler Engine**: Web crawling and analysis
- **Task Queue**: Asynchronous processing
- **Database**: Data persistence and relationships

### 2. Scalability
- **Horizontal Scaling**: Stateless services that can be replicated
- **Async Processing**: Non-blocking I/O operations
- **Queue-based Architecture**: Decoupled task processing
- **Caching**: Redis for performance optimization

### 3. Security
- **Defense in Depth**: Multiple security layers
- **Principle of Least Privilege**: Minimal required permissions
- **Input Validation**: Comprehensive data validation
- **Audit Logging**: Complete audit trail

### 4. Observability
- **Structured Logging**: JSON logs with correlation IDs
- **Metrics Collection**: Prometheus metrics
- **Health Checks**: Comprehensive health monitoring
- **Distributed Tracing**: Request flow tracking

## System Components

### Frontend Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)            │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                │
│  ├── Authentication (Login, Register, Profile)             │
│  ├── Project Management (Create, Edit, List)               │
│  ├── Scan Management (Start, Monitor, Results)             │
│  ├── Dashboard (Overview, Statistics)                      │
│  └── Reports (Export, Visualization)                       │
├─────────────────────────────────────────────────────────────┤
│  State Management:                                          │
│  ├── Redux Toolkit (Application State)                     │
│  ├── React Query (Server State)                            │
│  └── Supabase Realtime (Live Updates)                      │
├─────────────────────────────────────────────────────────────┤
│  UI Framework:                                              │
│  ├── Material-UI v5 (Components)                           │
│  ├── Custom Theme (Dark Mode)                              │
│  └── Responsive Design                                      │
└─────────────────────────────────────────────────────────────┘
```

**Technologies:**
- React 18+ with Hooks and Suspense
- TypeScript for type safety
- Material-UI v5 for consistent UI
- Redux Toolkit for state management
- React Query for server state
- Vite for fast development builds

**Key Features:**
- Real-time scan progress updates
- Responsive design for all devices
- Dark theme with accessibility support
- Comprehensive error handling
- Offline capability with service workers

### Backend API Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                    │
├─────────────────────────────────────────────────────────────┤
│  API Routes:                                                │
│  ├── /api/v1/auth/* (Authentication)                       │
│  ├── /api/v1/projects/* (Project Management)               │
│  ├── /api/v1/scans/* (Scan Operations)                     │
│  ├── /api/v1/results/* (Results & Reports)                 │
│  └── /api/v1/health (Health Checks)                        │
├─────────────────────────────────────────────────────────────┤
│  Middleware:                                                │
│  ├── Authentication (JWT Validation)                       │
│  ├── Rate Limiting (Per User/IP)                           │
│  ├── CORS (Cross-Origin Requests)                          │
│  ├── Logging (Request/Response)                            │
│  └── Metrics (Prometheus)                                  │
├─────────────────────────────────────────────────────────────┤
│  Services:                                                  │
│  ├── Project Service (Business Logic)                      │
│  ├── Scan Service (Orchestration)                          │
│  ├── Storage Service (File Management)                     │
│  └── Notification Service (Alerts)                         │
└─────────────────────────────────────────────────────────────┘
```

**Technologies:**
- FastAPI for high-performance API
- Pydantic v2 for data validation
- SQLAlchemy 2.0 with async support
- Supabase Python SDK
- JWT for authentication
- Prometheus for metrics

**Key Features:**
- OpenAPI/Swagger documentation
- Async/await throughout
- Comprehensive input validation
- Role-based access control
- Rate limiting and throttling

### Crawler Engine

```
┌─────────────────────────────────────────────────────────────┐
│                    Crawler Engine                           │
├─────────────────────────────────────────────────────────────┤
│  Core Components:                                           │
│  ├── Spider (URL Discovery)                                │
│  ├── Parser (Content Extraction)                           │
│  ├── Fingerprinter (Technology Detection)                  │
│  ├── Normalizer (URL Canonicalization)                     │
│  └── Session Manager (Authentication)                      │
├─────────────────────────────────────────────────────────────┤
│  Features:                                                  │
│  ├── Async HTTP Requests (aiohttp)                         │
│  ├── Rate Limiting (Per Domain)                            │
│  ├── Robots.txt Compliance                                 │
│  ├── Session Persistence                                   │
│  ├── Error Handling & Retries                              │
│  └── Progress Tracking                                      │
├─────────────────────────────────────────────────────────────┤
│  Analysis:                                                  │
│  ├── Form Extraction & Analysis                            │
│  ├── Technology Fingerprinting                             │
│  ├── Security Header Analysis                              │
│  ├── Link Discovery & Classification                       │
│  └── Content Analysis                                       │
└─────────────────────────────────────────────────────────────┘
```

**Technologies:**
- aiohttp for async HTTP requests
- BeautifulSoup4 for HTML parsing
- asyncio for concurrency management
- Regular expressions for pattern matching
- Custom fingerprinting database

**Key Features:**
- Configurable crawl depth and scope
- Intelligent rate limiting
- Technology detection (CMS, frameworks, libraries)
- Form analysis with CSRF detection
- Security header evaluation

### Task Queue System

```
┌─────────────────────────────────────────────────────────────┐
│                    Task Queue (Celery)                      │
├─────────────────────────────────────────────────────────────┤
│  Task Types:                                                │
│  ├── Crawler Tasks (Long-running scans)                    │
│  ├── Report Tasks (PDF/CSV generation)                     │
│  ├── Notification Tasks (Email/Slack)                      │
│  └── Cleanup Tasks (Data retention)                        │
├─────────────────────────────────────────────────────────────┤
│  Queue Management:                                          │
│  ├── Priority Queues (High/Normal/Low)                     │
│  ├── Task Routing (By type/priority)                       │
│  ├── Retry Logic (Exponential backoff)                     │
│  ├── Dead Letter Queue (Failed tasks)                      │
│  └── Monitoring (Task status/metrics)                      │
├─────────────────────────────────────────────────────────────┤
│  Workers:                                                   │
│  ├── Crawler Workers (CPU intensive)                       │
│  ├── Report Workers (I/O intensive)                        │
│  ├── Beat Scheduler (Periodic tasks)                       │
│  └── Flower Monitor (Web UI)                               │
└─────────────────────────────────────────────────────────────┘
```

**Technologies:**
- Celery for distributed task processing
- Redis as message broker
- RabbitMQ for complex routing (optional)
- Flower for monitoring
- Custom task serializers

**Key Features:**
- Distributed task processing
- Task prioritization and routing
- Automatic retry with backoff
- Real-time progress updates
- Comprehensive monitoring

### Database Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    Database (Supabase)                      │
├─────────────────────────────────────────────────────────────┤
│  Core Tables:                                               │
│  ├── profiles (User profiles)                              │
│  ├── projects (Scan projects)                              │
│  ├── scan_sessions (Scan instances)                        │
│  ├── discovered_urls (Crawled URLs)                        │
│  ├── extracted_forms (Form data)                           │
│  └── technology_fingerprints (Tech stack)                  │
├─────────────────────────────────────────────────────────────┤
│  Features:                                                  │
│  ├── Row Level Security (RLS)                              │
│  ├── Real-time Subscriptions                               │
│  ├── Automatic Backups                                     │
│  ├── Connection Pooling                                    │
│  ├── Read Replicas                                         │
│  └── Point-in-time Recovery                                │
├─────────────────────────────────────────────────────────────┤
│  Indexes & Optimization:                                    │
│  ├── Primary Keys (UUID)                                   │
│  ├── Foreign Key Indexes                                   │
│  ├── Composite Indexes                                     │
│  ├── Partial Indexes                                       │
│  └── Query Optimization                                     │
└─────────────────────────────────────────────────────────────┘
```

**Technologies:**
- PostgreSQL 15+ (via Supabase)
- Row Level Security (RLS)
- Real-time subscriptions
- Automatic scaling
- Built-in authentication

**Key Features:**
- Multi-tenant data isolation
- Real-time data synchronization
- Automatic backups and recovery
- Performance optimization
- ACID compliance

## Data Flow Architecture

### 1. User Authentication Flow

```
User → Frontend → Supabase Auth → JWT Token → Backend API
  ↓
Database (RLS policies applied based on user context)
```

### 2. Scan Creation Flow

```
User Request → Frontend → Backend API → Validation → Database
     ↓
Task Queue → Celery Worker → Crawler Engine → Results → Database
     ↓
Real-time Updates → Supabase Realtime → Frontend → User
```

### 3. Crawling Process Flow

```
Start Scan → Initialize Crawler → Load Configuration
     ↓
Discover URLs → Parse Content → Extract Data → Analyze Technology
     ↓
Store Results → Update Progress → Send Notifications
     ↓
Generate Reports → Complete Scan → Cleanup Resources
```

## Security Architecture

### 1. Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│  Frontend Security:                                         │
│  ├── JWT Token Management                                   │
│  ├── Automatic Token Refresh                               │
│  ├── Secure Storage (httpOnly cookies)                     │
│  └── CSRF Protection                                        │
├─────────────────────────────────────────────────────────────┤
│  API Security:                                              │
│  ├── JWT Validation Middleware                             │
│  ├── Rate Limiting (Per user/IP)                           │
│  ├── Input Validation (Pydantic)                           │
│  ├── SQL Injection Prevention                              │
│  └── XSS Protection                                         │
├─────────────────────────────────────────────────────────────┤
│  Database Security:                                         │
│  ├── Row Level Security (RLS)                              │
│  ├── Encrypted Connections (SSL)                           │
│  ├── Parameterized Queries                                 │
│  ├── Audit Logging                                         │
│  └── Backup Encryption                                      │
└─────────────────────────────────────────────────────────────┘
```

### 2. Network Security

```
Internet → CDN/WAF → Load Balancer → API Gateway → Services
    ↓
SSL/TLS Termination → Rate Limiting → Authentication → Authorization
    ↓
Internal Network (VPC) → Database (Private Subnet)
```

### 3. Data Protection

- **Encryption at Rest**: Database and file storage encryption
- **Encryption in Transit**: TLS 1.3 for all communications
- **Key Management**: Secure key rotation and storage
- **Data Masking**: Sensitive data protection in logs
- **Access Controls**: Principle of least privilege

## Performance Architecture

### 1. Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layers                           │
├─────────────────────────────────────────────────────────────┤
│  Browser Cache:                                             │
│  ├── Static Assets (CSS, JS, Images)                       │
│  ├── API Responses (Short TTL)                             │
│  └── User Preferences                                       │
├─────────────────────────────────────────────────────────────┤
│  CDN Cache:                                                 │
│  ├── Static Content Distribution                           │
│  ├── Geographic Edge Locations                             │
│  └── Cache Invalidation                                     │
├─────────────────────────────────────────────────────────────┤
│  Application Cache (Redis):                                 │
│  ├── Session Data                                          │
│  ├── Frequently Accessed Data                              │
│  ├── Rate Limiting Counters                                │
│  └── Task Queue Messages                                    │
├─────────────────────────────────────────────────────────────┤
│  Database Cache:                                            │
│  ├── Query Result Cache                                     │
│  ├── Connection Pooling                                     │
│  └── Read Replicas                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Scaling Strategy

**Horizontal Scaling:**
- Stateless API servers
- Load balancer distribution
- Auto-scaling based on metrics
- Database read replicas

**Vertical Scaling:**
- Resource optimization
- Performance profiling
- Memory management
- CPU optimization

### 3. Performance Monitoring

```
Application Metrics → Prometheus → Grafana Dashboards
     ↓
Alerting Rules → Notification Channels (Slack, Email)
     ↓
Auto-scaling Triggers → Kubernetes HPA → Scale Services
```

## Deployment Architecture

### 1. Development Environment

```
Developer Machine:
├── Docker Compose (Local services)
├── Hot Reload (Frontend/Backend)
├── Test Database (PostgreSQL)
├── Mock Services
└── Debug Tools
```

### 2. Staging Environment

```
Staging Cluster:
├── Kubernetes Deployment
├── Reduced Resource Allocation
├── Staging Database
├── Integration Testing
└── Performance Testing
```

### 3. Production Environment

```
Production Cluster:
├── High Availability Setup
├── Load Balancing
├── Auto-scaling
├── Monitoring & Alerting
├── Backup & Recovery
└── Security Hardening
```

## Monitoring & Observability

### 1. Metrics Collection

```
┌─────────────────────────────────────────────────────────────┐
│                    Metrics Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  Application Metrics:                                       │
│  ├── API Response Times                                     │
│  ├── Request Rates                                          │
│  ├── Error Rates                                            │
│  ├── Crawler Performance                                    │
│  └── User Activity                                          │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Metrics:                                    │
│  ├── CPU/Memory Usage                                       │
│  ├── Disk I/O                                              │
│  ├── Network Traffic                                        │
│  ├── Database Performance                                   │
│  └── Queue Depth                                            │
├─────────────────────────────────────────────────────────────┤
│  Business Metrics:                                          │
│  ├── Active Users                                          │
│  ├── Scans Completed                                       │
│  ├── Data Processed                                        │
│  ├── Success Rates                                         │
│  └── Feature Usage                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Logging Strategy

```
Application Logs → Structured JSON → Log Aggregation (Loki)
     ↓
Log Processing → Search & Analysis → Alerting
     ↓
Dashboards → Visualization → Insights
```

### 3. Alerting Rules

- **Critical**: Service down, database unavailable
- **Warning**: High error rates, performance degradation
- **Info**: Deployment notifications, maintenance windows

## Disaster Recovery

### 1. Backup Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Backup Architecture                      │
├─────────────────────────────────────────────────────────────┤
│  Database Backups:                                          │
│  ├── Continuous WAL Archiving                              │
│  ├── Daily Full Backups                                    │
│  ├── Point-in-time Recovery                                │
│  └── Cross-region Replication                              │
├─────────────────────────────────────────────────────────────┤
│  Application Backups:                                       │
│  ├── Configuration Files                                   │
│  ├── Static Assets                                         │
│  ├── User Uploads                                          │
│  └── Generated Reports                                      │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Backups:                                    │
│  ├── Kubernetes Manifests                                  │
│  ├── Docker Images                                         │
│  ├── SSL Certificates                                      │
│  └── Monitoring Configuration                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Recovery Procedures

1. **Database Recovery**: Point-in-time restore from backups
2. **Service Recovery**: Rolling deployment with health checks
3. **Data Recovery**: File system restore from snapshots
4. **Network Recovery**: DNS failover and load balancer updates

### 3. Business Continuity

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Availability Target**: 99.9% uptime
- **Disaster Recovery Testing**: Monthly drills

## Technology Decisions

### 1. Framework Choices

**FastAPI vs Django/Flask:**
- ✅ Native async support
- ✅ Automatic OpenAPI documentation
- ✅ High performance
- ✅ Modern Python features

**React vs Vue/Angular:**
- ✅ Large ecosystem
- ✅ TypeScript integration
- ✅ Material-UI compatibility
- ✅ Team expertise

**Supabase vs Traditional Database:**
- ✅ Built-in authentication
- ✅ Real-time subscriptions
- ✅ Automatic scaling
- ✅ Reduced operational overhead

### 2. Architecture Patterns

**Microservices vs Monolith:**
- ✅ Independent scaling
- ✅ Technology diversity
- ✅ Team autonomy
- ❌ Increased complexity

**Event-Driven vs Request-Response:**
- ✅ Loose coupling
- ✅ Scalability
- ✅ Resilience
- ❌ Eventual consistency

### 3. Trade-offs

**Performance vs Consistency:**
- Eventual consistency for non-critical data
- Strong consistency for user data
- Caching for performance optimization

**Security vs Usability:**
- Multi-factor authentication optional
- Session timeout balancing
- Progressive security measures

**Cost vs Reliability:**
- Auto-scaling for cost optimization
- Redundancy for critical components
- Monitoring for proactive management

## Future Architecture Considerations

### 1. Scalability Improvements

- **Database Sharding**: Horizontal database partitioning
- **Microservices**: Further service decomposition
- **Edge Computing**: Distributed crawling nodes
- **Caching**: Advanced caching strategies

### 2. Technology Evolution

- **AI/ML Integration**: Intelligent vulnerability detection
- **GraphQL**: Flexible API queries
- **Serverless**: Function-as-a-Service adoption
- **WebAssembly**: Client-side processing

### 3. Operational Excellence

- **GitOps**: Infrastructure as code
- **Chaos Engineering**: Resilience testing
- **Service Mesh**: Advanced networking
- **Observability**: Enhanced monitoring

---

This architecture documentation provides a comprehensive overview of the system design, components, and technical decisions. It serves as a reference for developers, operators, and stakeholders to understand the system's structure and behavior.