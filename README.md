# APOLLO

**Autonomous Productivity & Optimization Life Logic Orchestrator**

A multi-agent AI system for personal productivity and life optimization, built as a portfolio capstone project.

---

## Project Overview

APOLLO is a sophisticated productivity system that combines:
- Multi-agent AI architecture for task delegation and optimization
- Real-time tracking and analytics
- Strategic advisory capabilities
- Natural language interface

**Note:** This project was originally named ATLAS but was renamed to APOLLO on 2025-10-22 to differentiate from OpenAI's Atlas browser product.

---

## Tech Stack

**Backend:**
- FastAPI (Python) - REST API framework
- Supabase (PostgreSQL) - Database and real-time sync
- Pydantic - Data validation and serialization
- OpenAI Agents SDK - Multi-agent orchestration

**Frontend (Planned):**
- Next.js 15 - React framework with App Router
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Styling

**Infrastructure:**
- Docker - Containerization
- Vercel - Frontend deployment
- Render/Railway - Backend deployment

---

## Current Status

**Module 1.2 Complete** (as of 2025-10-22):
- ✅ PostgreSQL database with Supabase
- ✅ User management endpoints (POST /users, GET /users/{id})
- ✅ Pydantic models with validation
- ✅ CORS configuration for frontend integration
- ✅ Environment variable management
- ✅ Comprehensive error handling

**Next:** Module 1.3 - Task Management Endpoints

---

## Development Philosophy

- **60% Manual Coding** - Interview readiness and deep understanding
- **40% AI Assistance** - Productivity and best practices
- **Quality Gates** - Verify learning at each module completion
- **Test-First** - Comprehensive testing before feature expansion

---

## Getting Started

### Prerequisites
- Python 3.13+
- Supabase account (free tier)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd atlas-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Running the API

```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access the API
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### Testing

```bash
# Run tests (when implemented)
pytest

# Check code coverage
pytest --cov=app
```

---

## API Endpoints

### Users

**Create User**
```bash
POST /users
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Get User**
```bash
GET /users/{user_id}
```

**Health Check**
```bash
GET /health
```

---

## Project Structure

```
apollo-project/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── db/
│   │   └── supabase_client.py  # Database connection
│   └── models/
│       ├── user.py          # User Pydantic model
│       └── task.py          # Task Pydantic model
├── .env                     # Environment variables (not in git)
├── .gitignore
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Database Schema

### Users Table
- `id` (UUID) - Primary key
- `email` (TEXT) - Unique, validated email
- `created_at` (TIMESTAMPTZ) - Auto-generated
- `updated_at` (TIMESTAMPTZ) - Auto-generated

### Tasks Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `title` (TEXT) - Task title
- `description` (TEXT) - Optional description
- `status` (TEXT) - pending | in_progress | completed
- `created_at` (TIMESTAMPTZ) - Auto-generated
- `updated_at` (TIMESTAMPTZ) - Auto-generated

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [x] Module 1.1: FastAPI Setup
- [x] Module 1.2: Database Integration
- [ ] Module 1.3: Task Management
- [ ] Module 1.4: User Authentication

### Phase 2: Core Features (Weeks 5-8)
- [ ] Module 2.1: Goal Management
- [ ] Module 2.2: Time Tracking
- [ ] Module 2.3: Analytics Dashboard
- [ ] Module 2.4: Next.js Frontend

### Phase 3: AI Agents (Weeks 9-12)
- [ ] Module 3.1: Task Advisor Agent
- [ ] Module 3.2: Strategic Planner Agent
- [ ] Module 3.3: Multi-Agent Orchestration
- [ ] Module 3.4: Natural Language Interface

---

## Contributing

This is a personal portfolio project. However, feedback and suggestions are welcome via issues.

---

## License

MIT License - See LICENSE file for details

---

## Contact

[Your Name]
- GitHub: [your-github]
- LinkedIn: [your-linkedin]
- Portfolio: [your-portfolio]

---

**Built with ☕ and 🎯 in Vancouver, BC**
