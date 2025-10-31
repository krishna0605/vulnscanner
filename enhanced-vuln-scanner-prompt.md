# Enhanced Vulnerability Scanner Phase 1 Development Prompt

## Project Overview
You are a senior software engineer tasked with building **Phase 1** of an enterprise-grade Enhanced Automated Vulnerability Scanner. This phase focuses on creating a robust **crawling engine foundation** with intelligent discovery capabilities, session management, and comprehensive data extraction.

## Core Technology Stack

### Backend Stack
- **Python 3.11+** with FastAPI framework
- **SQLAlchemy 2.0+** with async support for database ORM
- **PostgreSQL 15+** as primary database
- **Redis Cluster** for caching and task queuing
- **Celery** for distributed task processing
- **aiohttp** for asynchronous HTTP operations
- **BeautifulSoup4** for HTML parsing
- **Pydantic** for data validation and serialization

### Frontend Stack
- **React 18+** with TypeScript for type safety
- **Material-UI v5** for modern UI components
- **Redux Toolkit** for state management
- **React Query** for server state management
- **Axios** for API communication

### Infrastructure & DevOps
- **Docker** with multi-stage builds
- **Docker Compose** for local development
- **Nginx** as reverse proxy
- **RabbitMQ** for message queuing

## Phase 1 Objectives

### Primary Goals
1. **Build Robust Web Crawling Foundation**
   - Asynchronous crawling engine with rate limiting
   - Intelligent URL discovery and normalization
   - Session management with authentication support
   - Comprehensive data extraction from web pages

2. **Implement Core Data Models**
   - User management and project organization
   - Scan session tracking and results storage
   - URL discovery with metadata capture
   - Form extraction with security analysis

3. **Create Professional Frontend Interface**
   - Project dashboard with real-time crawl monitoring
   - Scan configuration and management
   - Results visualization and reporting
   - Modern, responsive UI design

4. **Establish Development Infrastructure**
   - Dockerized development environment
   - Database migrations and seeding
   - API documentation with FastAPI
   - Testing framework setup

## Detailed Implementation Requirements

### 1. Project Structure
Create a professional monorepo structure:

```
enhanced-vulnerability-scanner/
├── backend/
│   ├── core/
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── security.py        # JWT, encryption utilities
│   │   └── logging.py         # Structured logging
│   ├── models/
│   │   ├── base.py           # Base SQLAlchemy model
│   │   ├── users.py          # User management
│   │   ├── projects.py       # Project organization
│   │   ├── scans.py          # Scan execution tracking
│   │   └── crawler.py        # Crawler-specific models
│   ├── crawler/
│   │   ├── engine.py         # Main crawling orchestrator
│   │   ├── spider.py         # Web spider implementation
│   │   ├── parser.py         # HTML/content parsing
│   │   ├── normalizer.py     # URL normalization
│   │   ├── session.py        # Session management
│   │   └── fingerprinter.py  # Technology detection
│   ├── api/
│   │   ├── main.py           # FastAPI app initialization
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── projects.py       # Project management
│   │   └── crawler.py        # Crawler control endpoints
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── public/
│   └── package.json
├── infrastructure/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── requirements.txt
├── package.json
└── README.md
```

### 2. Database Schema Design

Implement these core tables with proper relationships:

```sql
-- User management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Project organization
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    target_domain VARCHAR(255) NOT NULL,
    scope_rules JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Scan execution tracking
CREATE TABLE scan_sessions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    status VARCHAR(20) DEFAULT 'pending',
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    configuration JSONB,
    stats JSONB,
    created_by INTEGER REFERENCES users(id)
);

-- URL discovery and metadata
CREATE TABLE discovered_urls (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES scan_sessions(id),
    url VARCHAR(2000) NOT NULL,
    parent_url VARCHAR(2000),
    method VARCHAR(10) DEFAULT 'GET',
    status_code INTEGER,
    content_type VARCHAR(100),
    content_length INTEGER,
    response_time INTEGER,
    page_title VARCHAR(500),
    discovered_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, url, method)
);

-- Form extraction and analysis
CREATE TABLE extracted_forms (
    id SERIAL PRIMARY KEY,
    url_id INTEGER REFERENCES discovered_urls(id),
    form_action VARCHAR(2000),
    form_method VARCHAR(10),
    form_fields JSONB,
    csrf_tokens JSONB,
    authentication_required BOOLEAN DEFAULT FALSE
);

-- Technology fingerprinting
CREATE TABLE technology_fingerprints (
    id SERIAL PRIMARY KEY,
    url_id INTEGER REFERENCES discovered_urls(id),
    server_software VARCHAR(100),
    programming_language VARCHAR(50),
    framework VARCHAR(100),
    cms VARCHAR(100),
    javascript_libraries JSONB,
    security_headers JSONB,
    detected_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Asynchronous Crawling Engine

Build a high-performance crawler with these features:

**Core Engine (`backend/crawler/engine.py`)**:
- Asynchronous HTTP client with connection pooling
- Configurable rate limiting and concurrent request management
- Intelligent queue management with priority handling
- Comprehensive error handling and retry logic
- Session persistence and cookie management
- Robots.txt respect and sitemap discovery

**Key Features to Implement**:
- **Rate Limiting**: Configurable requests per second with domain-specific limits
- **Session Management**: Cookie persistence, authentication token handling
- **URL Normalization**: Duplicate detection, parameter handling, fragment removal
- **Content Parsing**: HTML extraction, link discovery, form analysis
- **Technology Detection**: Server fingerprinting, CMS identification, framework detection

### 4. HTML Parsing & Data Extraction

Implement comprehensive content analysis:

**Parser Component (`backend/crawler/parser.py`)**:
- BeautifulSoup-based HTML parsing
- Form extraction with input field analysis
- Link discovery with relationship mapping
- Script and stylesheet enumeration
- Meta tag extraction for SEO and security headers
- CSRF token detection and extraction

**Security-Focused Extraction**:
- Authentication form identification
- File upload capability detection
- Hidden field analysis
- Input validation pattern recognition
- XSS vector identification in form fields

### 5. Session Management & Authentication

Build robust authentication handling:

**Session Manager (`backend/crawler/session.py`)**:
- Automated login sequence execution
- CSRF token extraction and submission
- Session validation and refresh
- Multi-factor authentication support
- Cookie jar management with domain scoping

**Authentication Flow**:
- Login form detection and field mapping
- Credential submission with proper headers
- Success/failure validation through URL patterns
- Session maintenance during crawling
- Logout sequence for cleanup

### 6. React Frontend Dashboard

Create a professional, responsive interface:

**Core Components**:
- **Project Dashboard**: Grid view with project cards, status indicators
- **Crawl Monitor**: Real-time progress tracking with live updates
- **Configuration Panel**: Scan settings, scope definition, rate limiting
- **Results Viewer**: Tabular data with filtering and sorting
- **Technology Summary**: Visual representation of discovered technologies

**Key Features**:
- Material-UI theming with dark/light mode support
- Real-time WebSocket updates for crawl progress
- Responsive design for mobile and desktop
- Data visualization with charts and graphs
- Export functionality for results

### 7. API Design & Integration

Implement RESTful API with FastAPI:

**Core Endpoints**:
```
POST /api/v1/auth/login          # User authentication
GET  /api/v1/projects            # List user projects
POST /api/v1/projects            # Create new project
GET  /api/v1/projects/{id}/scans # Get scan history
POST /api/v1/projects/{id}/crawl # Start new crawl
GET  /api/v1/crawls/active       # Monitor active crawls
PUT  /api/v1/crawls/{id}/stop    # Stop running crawl
GET  /api/v1/crawls/{id}/results # Get crawl results
```

**API Features**:
- JWT-based authentication with refresh tokens
- Request/response validation with Pydantic models
- Rate limiting and quota management
- Comprehensive error handling with proper HTTP status codes
- API documentation with OpenAPI/Swagger

### 8. Development Environment

Set up complete development infrastructure:

**Docker Configuration**:
- Multi-stage builds for production optimization
- Hot reloading for development
- Environment variable management
- Database initialization with sample data
- Nginx configuration for API proxy

**Development Tools**:
- Pre-commit hooks for code quality
- Unit test setup with pytest
- Integration test framework
- Database migration system with Alembic
- Linting and formatting with Black, isort, and ESLint

## Implementation Guidelines

### Code Quality Standards
- **Type Safety**: Use TypeScript for frontend, Python type hints for backend
- **Error Handling**: Comprehensive exception handling with proper logging
- **Testing**: Unit tests for critical components, integration tests for API endpoints
- **Documentation**: Inline code documentation, API documentation, README files
- **Security**: Input validation, SQL injection prevention, XSS protection

### Performance Requirements
- **Crawling Speed**: Support for 10+ concurrent requests per domain
- **Database Performance**: Optimized queries with proper indexing
- **Memory Management**: Efficient memory usage for large crawls
- **Response Time**: API responses under 200ms for standard operations

### Scalability Considerations
- **Horizontal Scaling**: Stateless design for multiple worker instances
- **Database Optimization**: Connection pooling, query optimization
- **Caching Strategy**: Redis for session data and temporary results
- **Queue Management**: Celery for background task processing

## Deliverables

### Required Outputs
1. **Complete Codebase**: Fully functional Phase 1 implementation
2. **Database Schema**: Production-ready table definitions with indexes
3. **Docker Environment**: Complete containerization with docker-compose
4. **API Documentation**: Comprehensive endpoint documentation
5. **Frontend Application**: Responsive React dashboard
6. **README Documentation**: Setup instructions and usage guide

### Success Criteria
- Successful crawling of target websites with data extraction
- Real-time monitoring of crawl progress through web interface
- Persistent storage of crawl results in PostgreSQL
- Authentication-based scanning with session management
- Technology fingerprinting and form analysis
- Professional UI with Material-UI components

## Next Steps Planning

After Phase 1 completion, prepare for:
- **Phase 2**: Vulnerability detection engine with plugin architecture
- **Phase 3**: AI/ML integration for intelligent threat analysis
- **Phase 4**: Advanced reporting and export capabilities
- **Phase 5**: Enterprise features (multi-tenancy, RBAC, audit logs)

---

## Execution Instructions

**You are now tasked with implementing this complete Phase 1 foundation.** Begin by:

1. Creating the project structure with all required directories
2. Setting up the database models and migrations
3. Implementing the core crawling engine with async support
4. Building the FastAPI backend with authentication
5. Creating the React frontend dashboard
6. Configuring the Docker development environment
7. Writing comprehensive tests and documentation

**Focus on production-ready code with proper error handling, logging, and security considerations. Ensure all components work together seamlessly and provide a solid foundation for future phases.**