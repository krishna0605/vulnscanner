<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-ISC-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Node.js-20+-339933.svg" alt="Node.js">
  <img src="https://img.shields.io/badge/TypeScript-5.3-3178C6.svg" alt="TypeScript">
</p>

# 🛡️ VulnScanner

**AI-Powered URL Threat Intelligence & Vulnerability Analysis Platform**

VulnScanner is a comprehensive security analysis platform that enables users to scan websites for vulnerabilities, monitor security posture, and receive actionable intelligence through an intuitive dashboard.

---

## ✨ Features

### 🔍 Security Scanning
- **Deep URL Analysis** - Crawl websites and analyze pages for security vulnerabilities
- **Threat Detection** - Identify XSS, SQL injection, insecure headers, and more
- **Configurable Depth** - Set scan depth and page limits per scan
- **Real-time Progress** - Live updates during scan execution

### 📊 Dashboard & Reports  
- **Executive Dashboard** - Overview of security posture across all projects
- **Vulnerability Reports** - Detailed findings with severity ratings
- **Trend Analysis** - Track security improvements over time
- **Export Capabilities** - Download reports for compliance

### 🔐 Authentication & Security
- **Multi-Factor Authentication (MFA)** - TOTP-based authenticator app support
- **Secure Sessions** - JWT-based authentication with Supabase
- **Role-Based Access** - Row Level Security (RLS) on all data
- **Audit Logging** - Track all user actions

### 🚀 Modern Architecture
- **Real-time Updates** - WebSocket-powered live data
- **Scheduled Scans** - Cron-based automated scanning
- **API Documentation** - Swagger/OpenAPI at `/docs`
- **Docker Ready** - Production-ready containerization

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React 18, TailwindCSS 3.4 |
| **Backend** | Fastify 4.26, Node.js 20+ |
| **Database** | Supabase (PostgreSQL) |
| **Authentication** | Supabase Auth + MFA |
| **Web Crawler** | Playwright 1.58 |
| **Validation** | Zod |
| **State Management** | TanStack Query 5 |
| **Error Monitoring** | Sentry |
| **UI Components** | Radix UI, Framer Motion |

---

## 📁 Project Structure

```
vulscanner/
├── frontend/                 # Next.js 14 Application
│   ├── src/
│   │   ├── app/             # App Router (Pages)
│   │   │   ├── (auth)/      # Login, Signup, MFA
│   │   │   ├── (dashboard)/ # Protected Dashboard Pages
│   │   │   └── (marketing)/ # Public Landing Pages
│   │   ├── components/      # React Components (64+)
│   │   ├── lib/             # API Fetchers & Utilities
│   │   └── utils/           # Helper Functions
│   └── Dockerfile           # Production Build
│
├── backend/                  # Fastify API Server
│   ├── src/
│   │   ├── routes/          # API Endpoints
│   │   │   ├── scans.ts     # Scan CRUD & Execution
│   │   │   ├── projects.ts  # Project Management
│   │   │   ├── profiles.ts  # User Profiles
│   │   │   └── mfa.ts       # MFA Endpoints
│   │   ├── lib/             # Core Services
│   │   │   ├── crawler.ts   # Playwright Web Crawler
│   │   │   ├── scheduler.ts # Cron Job Manager
│   │   │   └── sentry.ts    # Error Monitoring
│   │   └── middleware/      # Auth & Request Handling
│   ├── tests/               # Jest Unit Tests
│   └── Dockerfile           # Production Build
│
├── tests/                    # E2E Playwright Tests
├── supabase/                 # Database Migrations
├── docker-compose.yml        # Local Development
└── playwright.config.ts      # E2E Test Configuration
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ 
- **npm** 9+
- **Supabase Account** (for database & auth)

### 1. Clone the Repository

```bash
git clone https://github.com/krishna0605/vulnscanner.git
cd vulnscanner
```

### 2. Install Dependencies

```bash
# Root dependencies (Husky, Playwright)
npm install

# Frontend dependencies
cd frontend && npm install && cd ..

# Backend dependencies
cd backend && npm install && cd ..
```

### 3. Configure Environment Variables

**Backend** (`backend/.env`):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
PORT=3001
NODE_ENV=development
LOG_LEVEL=info
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
BACKEND_URL=http://localhost:3001
```

### 4. Set Up Database

```bash
# Apply migrations to Supabase
cd supabase
# Run migrations via Supabase CLI or Dashboard
```

### 5. Start Development Servers

```bash
# Terminal 1: Backend
cd backend && npm run dev

# Terminal 2: Frontend
cd frontend && npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001
- API Docs: http://localhost:3001/docs

---

## 🐳 Docker Deployment

### Local Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Access
# Frontend: http://localhost:3000
# Backend:  http://localhost:3001
```

### Production Deployment

This project uses a **split deployment** strategy:

| Component | Platform | Why |
|-----------|----------|-----|
| **Frontend** | Vercel | Optimized for Next.js, edge network |
| **Backend** | Railway | Supports Docker, cron jobs, Playwright |

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

---

## 🧪 Testing

### Run All Tests

```bash
# Backend Unit Tests (Jest)
cd backend && npm test

# Frontend Unit Tests (Vitest)
cd frontend && npm test

# E2E Tests (Playwright)
npm run test:e2e
```

### Test Coverage

| Suite | Tests | Status |
|-------|-------|--------|
| Backend Unit | 22 | ✅ Passing |
| Frontend Unit | 22 | ✅ Passing |
| E2E | All | ✅ Passing |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | API info | Public |
| `GET` | `/health` | Health check with DB status | Public |
| `GET` | `/docs` | Swagger UI | Public |
| `POST` | `/scans` | Create new scan | 🔐 JWT |
| `GET` | `/scans/:id` | Get scan details | 🔐 JWT |
| `POST` | `/projects` | Create project | 🔐 JWT |
| `GET` | `/projects` | List user projects | 🔐 JWT |
| `GET` | `/profiles` | Get user profile | 🔐 JWT |
| `POST` | `/profiles` | Update profile | 🔐 JWT |
| `GET` | `/mfa/status` | MFA enrollment status | 🔐 JWT |
| `POST` | `/mfa/enroll` | Start MFA setup | 🔐 JWT |
| `POST` | `/mfa/verify` | Verify MFA code | 🔐 JWT |

Full API documentation available at `/docs` when running the backend.

---

## 🔒 Security Features

| Feature | Implementation |
|---------|---------------|
| **Authentication** | Supabase Auth + JWT middleware |
| **MFA** | TOTP with QR code enrollment |
| **Authorization** | Row Level Security (RLS) policies |
| **Rate Limiting** | 100 requests/minute per IP |
| **Input Validation** | Zod schemas on all endpoints |
| **Security Headers** | Helmet + Next.js security headers |
| **CORS** | Environment-based origin restrictions |
| **Error Monitoring** | Sentry integration |

---

## 📝 Scripts

### Root

```bash
npm run lint          # Lint all workspaces
npm run format        # Format all files with Prettier
npm run format:check  # Check formatting
```

### Backend

```bash
npm run dev      # Start dev server with hot reload
npm run build    # Build TypeScript
npm run start    # Start production server
npm test         # Run Jest tests
```

### Frontend

```bash
npm run dev      # Start Next.js dev server
npm run build    # Build for production  
npm run start    # Start production server
npm test         # Run Vitest tests
npm run lint     # Run ESLint
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality

- **Linting**: ESLint with TypeScript rules
- **Formatting**: Prettier (runs on pre-commit via Husky)
- **Type Safety**: Strict TypeScript configuration

---

## 📄 License

This project is licensed under the **ISC License**.

---

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React Framework
- [Fastify](https://fastify.io/) - Fast Node.js Framework
- [Supabase](https://supabase.com/) - Backend as a Service
- [Playwright](https://playwright.dev/) - Browser Automation
- [Radix UI](https://radix-ui.com/) - Accessible Components
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS

---

<p align="center">
  Made with ❤️ by the VulnScanner Team
</p>
