# Project Guide: Enhanced Vulnerability Scanner

This document provides a comprehensive overview of the Enhanced Vulnerability Scanner project, including its architecture, technology stack, and setup instructions.

## 1. Project Overview

The Enhanced Vulnerability Scanner is a production-ready web application designed to scan for vulnerabilities in web applications. It features a modern, scalable architecture with a separate frontend and backend, a task queue for asynchronous jobs, and a comprehensive monitoring solution.

### 1.1. Key Features

- **Intelligent Web Crawling**: Advanced async crawler with rate limiting and scope management.
- **Technology Detection**: Comprehensive fingerprinting of web technologies, frameworks, and CMS.
- **Form Analysis**: Detailed extraction and analysis of web forms, including CSRF detection.
- **Security Headers**: Analysis of security headers and best practices compliance.
- **Real-time Monitoring**: Live scan progress with WebSocket updates.
- **Comprehensive Reporting**: Multiple export formats (JSON, CSV, PDF, HTML).

## 2. Architecture

The project follows a microservices-based architecture, with the following key components:

- **Frontend**: A React-based single-page application that provides the user interface.
- **Backend**: A FastAPI-based application that exposes a RESTful API for the frontend and manages the scanning process.
- **Database**: A PostgreSQL database for storing application data.
- **Task Queue**: Celery with RabbitMQ as the message broker for handling long-running scanning tasks asynchronously.
- **Cache**: Redis for caching frequently accessed data and as a result backend for Celery.
- **Monitoring**: A combination of Prometheus and Grafana for monitoring application metrics and performance.

The `docker-compose.yml` file defines the services and their interactions.

## 3. Technology Stack

### 3.1. Backend

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0 with async support
- **Task Queue**: Celery with RabbitMQ broker and Redis result backend
- **HTTP Client**: aiohttp for async web requests
- **Parser**: BeautifulSoup4 for HTML parsing
- **Validation**: Pydantic v2 for data validation
- **Database**: PostgreSQL (or SQLite for local development)
- **Authentication**: Supabase Auth with JWT tokens (optional)

### 3.2. Frontend

- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI v5 with custom theming
- **State Management**: Redux Toolkit + React Query
- **Styling**: Tailwind CSS
- **Build Tool**: Vite with hot module replacement
- **Testing**: Vitest + React Testing Library

### 3.3. Infrastructure

- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes with Helm charts
- **Monitoring**: Prometheus + Grafana + Loki
- **CI/CD**: GitHub Actions with automated testing
- **Load Balancing**: Nginx with SSL termination

## 4. Detailed File Structure

```
vulscanner/
├── .github/                # GitHub Actions workflows
├── backend/                # FastAPI backend application
│   ├── alembic/            # Alembic database migration scripts
│   ├── api/                # API endpoints and routes
│   │   ├── deps.py         # API dependencies
│   │   └── v1/             # API version 1
│   │       ├── endpoints/  # API endpoint definitions
│   │       └── router.py   # API router
│   ├── core/               # Core configuration and utilities
│   │   ├── config.py       # Application configuration
│   │   └── security.py     # Security-related functions
│   ├── crawler/            # Web crawling engine
│   │   ├── crawler.py      # Main crawler logic
│   │   └── utils.py        # Crawler utility functions
│   ├── db/                 # Database session and initialization
│   │   ├── base.py         # Base model for SQLAlchemy
│   │   ├── init_db.py      # Database initialization script
│   │   └── session.py      # Database session management
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic services
│   ├── tasks/              # Celery background tasks
│   │   ├── celery_app.py   # Celery application instance
│   │   └── tasks.py        # Celery task definitions
│   ├── tests/              # Test suites
│   │   ├── api/            # API tests
│   │   ├── core/           # Core functionality tests
│   │   └── utils/          # Test utilities
│   ├── alembic.ini         # Alembic configuration
│   ├── Dockerfile          # Dockerfile for the backend
│   ├── main.py             # Main application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── public/             # Public assets
│   ├── src/                # Frontend source code
│   │   ├── api/            # API client for the frontend
│   │   ├── app/            # Main application component and store
│   │   ├── assets/         # Static assets like images and fonts
│   │   ├── components/     # Reusable UI components
│   │   ├── features/       # Feature-based modules
│   │   ├── hooks/          # Custom React hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # Redux store and slices
│   │   ├── theme/          # Material-UI theme configuration
│   │   ├── types/          # TypeScript type definitions
│   │   ├── utils/          # Utility functions
│   │   ├── App.tsx         # Main application component
│   │   ├── index.tsx       # Application entry point
│   │   └── serviceWorker.ts# Service worker for PWA functionality
│   ├── Dockerfile          # Dockerfile for the frontend
│   ├── package.json        # Frontend dependencies and scripts
│   └── tsconfig.json       # TypeScript configuration
├── supabase_sql/           # SQL scripts for Supabase
│   ├── 01_extensions_and_types.sql
│   ├── 02_core_tables.sql
│   ├── ...
│   └── 11_security_fixes.sql
├── .env.example            # Example environment variables
├── docker-compose.yml      # Docker Compose configuration for development
├── docker-compose.prod.yml # Docker Compose configuration for production
├── Makefile                # Makefile for common commands
└── README.md               # Project README
```

## 5. Key Files Summary

- **`backend/main.py`**: The entry point for the FastAPI application. It initializes the app, includes the API routers, and sets up middleware.
- **`backend/core/config.py`**: Defines the application's configuration using Pydantic settings management. It loads settings from environment variables.
- **`backend/db/session.py`**: Manages the database session, providing a dependency for API endpoints to get a database session.
- **`backend/tasks/celery_app.py`**: The entry point for the Celery application. It configures Celery and discovers tasks.
- **`frontend/src/index.tsx`**: The entry point for the React application. It renders the root `App` component and sets up the Redux store.
- **`frontend/src/App.tsx`**: The main application component. It sets up the router and renders the different pages of the application.
- **`frontend/src/store/store.ts`**: Configures the Redux store, including combining reducers and setting up middleware.
- **`docker-compose.yml`**: Defines the services, networks, and volumes for the development environment.
- **`Makefile`**: Provides a set of commands for common development tasks, such as running the application, running tests, and linting the code.

## 6. Setup and Installation

### 6.1. Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 6.2. Development Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/vulscanner.git
    cd vulscanner
    ```

2.  **Environment Setup**:
    ```bash
    # Copy environment template
    cp .env.example .env

    # Edit environment variables in .env
    ```

3.  **Start the development environment**:
    ```bash
    make dev-setup
    make run-dev
    ```

### 6.3. Accessing the Application

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Grafana**: `http://localhost:3001` (admin/admin)
- **Prometheus**: `http://localhost:9090`

## 7. Development Guide

### 7.1. Backend Development

The backend is a standard FastAPI application. The main entry point is `backend/main.py`. API routes are defined in the `backend/api/` directory.

### 7.2. Frontend Development

The frontend is a React application. The main entry point is `frontend/src/index.tsx`. Components are located in `frontend/src/components/` and pages in `frontend/src/pages/`.

### 7.3. Available Commands

The `Makefile` provides several useful commands for development:

- `make install-dev`: Install development dependencies.
- `make run-dev`: Start the development environment.
- `make test`: Run all tests.
- `make lint`: Run code linters.
- `make format`: Format code.
- `make db-migrate`: Create a database migration.
- `make db-upgrade`: Apply database migrations.

For a full list of commands, run `make help`.