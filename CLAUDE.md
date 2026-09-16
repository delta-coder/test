# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cinema booking system with **two distinct implementations**:

1. **Django Application** (`book_movie_ticket/`): Traditional server-side rendered web app with SQLite database, admin interface, and Django templates
2. **FastAPI Backend** (`web/`): Modern API-first architecture with PostgreSQL/SQLite, JWT authentication, and likely a separate frontend

## Architecture Overview

### Django Implementation (`book_movie_ticket/`)
- **Technology Stack**: Django 5.0, SQLite, Python, HTML/CSS/JS templates
- **Database**: SQLite (db.sqlite3)
- **Authentication**: Django's built-in auth system with CustomUser model
- **Admin Interface**: Full Django admin with movie/room/seat/showtime/ticket management
- **Features**:
  - Seat auto-generation when rooms are created
  - Movie background folder creation
  - Demo data population scripts
  - LAN-based server setup (run_windows.bat, setup_windows.bat)

### FastAPI Implementation (`web/`)
- **Technology Stack**: FastAPI 0.115, SQLAlchemy, PostgreSQL/SQLite, Python
- **Database**: PostgreSQL (with SQLite fallback)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Architecture**: Clean API with routers (auth, movies, showtimes)
- **Features**:
  - Seat hold/temporary reservation system
  - Expired hold cleanup
  - Cookie-based authentication
  - Scalable microservice-ready design

### Common Domain Models
Both implementations share these core concepts:
- **Movie**: Film details (title, genre, duration, director, release date)
- **Room**: Cinema room with capacity
- **Seat**: Individual seats in rooms (auto-numbered 1..capacity)
- **Showtime**: Movie screenings with specific times
- **Ticket**: Seat reservations for showtimes
- **User**: Account management with roles (admin/standard)

## Development Setup

### Prerequisites
- Python 3.11+
- pip/virtual environment

### Django Development
1. Navigate to `book_movie_ticket/`
2. Activate virtual environment: `..\.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start server: `python manage.py runserver 0.0.0.0:8000`
6. Access: http://127.0.0.1:8000/

### FastAPI Development
1. Navigate to `web/`
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables (see .env.example)
4. Start server: `uvicorn api.index:app --reload`
5. Access API at `/api/` endpoints

## Testing

### Django Tests
Run from `book_movie_ticket/` directory:
- `python manage.py test` - Run all tests
- `python manage.py test <app_name>` - Run specific app tests

### FastAPI Tests
- Use pytest or FastAPI's test client
- Test authentication flows
- Test seat booking logic
- Test error handling and edge cases

## Building and Deployment

### Current Deployment
- **Vercel**: Configured for FastAPI (`web/vercel.json`)
- **Windows**: Batch scripts for local development (run_windows.bat, setup_windows.bat)
- **Docker**: Not configured yet

### Key Deployment Files
- `web/vercel.json`: Vercel deployment configuration
- `web/.env.example`: Environment variables template
- `requirements.txt` (web): Production dependencies

## Project Scripts

### Management Scripts
- `scripts/` directory contains:
  - `run_server_controlled.py`: Controlled server startup
  - `cinema_console.ps1`: Interactive admin console
  - `background_log.ps1`: Background logging

### Data Management
- `add_more_demo_data.py`: Populates demo data in Django
- `restore_demo_data.py`: Restores demo data
- `sync_movie_media.py`: Media synchronization
- `live_seat_holds.json`: Runtime seat hold state

## Future Development Considerations

### Technology Stack Options
- **Frontend**: JavaScript (React/Vue/Angular) for modern SPAs
- **Mobile**: React Native or Flutter for cross-platform
- **Database**: PostgreSQL for both implementations
- **API Gateway**: Could unify both implementations
- **Containerization**: Docker for consistent deployment

### API Design Notes
- FastAPI implementation has better separation of concerns
- JWT tokens with cookie/HttpOnly for security
- Seat hold mechanism with automatic expiration
- Clean OpenAPI specification

### Database Schema Differences
- **Django**: Simpler relationships, Django-specific fields
- **FastAPI**: More explicit SQLAlchemy relationships, additional constraints (SeatHold for temporary reservations)

## Development Workflow

### Development Commands
1. **Django Development**:
   - `python manage.py makemigrations` - Create migrations
   - `python manage.py migrate` - Apply migrations
   - `python manage.py createsuperuser` - Create admin user
   - `python manage.py runserver` - Start development server

2. **FastAPI Development**:
   - `uvicorn api.index:app --reload` - Start with hot reload
   - `pytest` - Run tests
   - `python -m pytest tests/` - Specific test directory

3. **Project Management**:
   - Scripts in `scripts/` for server management
   - Data population scripts in project root

## Key Files and Directories

### Django App Structure
```
book_movie_ticket/
├── book_movie_ticket/          # Settings, URLs, WSGI
├── book_movie_ticket_app/       # Main app (models, views, admin)
├── templates/                  # HTML templates
├── static/                     # Static assets
├── migrations/                 # Database migrations
└── db.sqlite3                 # SQLite database
```

### FastAPI App Structure
```
web/
├── api/                        # API implementation
│   ├── __init__.py            # Main FastAPI app
│   ├── auth.py                # Authentication utilities
│   ├── config.py              # Settings
│   ├── db.py                  # Database setup
│   ├── deps.py                # Dependency injection
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas
│   ├── seat_service.py        # Seat management logic
│   └── routers/               # API endpoints
│       ├── auth.py
│       ├── movies.py
│       └── showtimes.py
├── public/                     # Static files (css, images, js)
├── requirements.txt           # Dependencies
└── vercel.json               # Vercel deployment config
```

## Common Development Tasks

### For Adding New Features
1. **Identify** which implementation to extend (or both)
2. **Update** models in both projects if domain changes
3. **Add** API endpoints in FastAPI
4. **Update** Django views/templates
5. **Write** tests for both implementations
6. **Update** documentation

### For Bug Fixes
1. **Reproduce** in both implementations
2. **Identify** root cause (model differences, logic bugs)
3. **Fix** in both projects
4. **Test** thoroughly
5. **Document** the fix

### For Deployment to Vercel
1. **Build** FastAPI for production
2. **Configure** environment variables
3. **Test** deployment
4. **Update** Django for Vercel (or use as fallback)

## File Conventions

### Python
- Use SQLAlchemy 2.0 style in FastAPI
- Use Django ORM conventions in Django
- Type hints throughout
- Both projects follow PEP 8

### Database
- SQLite in Django (file-based)
- PostgreSQL preferred in FastAPI
- Migration files in Django
- SQLAlchemy models in FastAPI

### Authentication
- **Django**: Django's built-in auth
- **FastAPI**: JWT with bcrypt
- Both support admin users with special privileges

## Future Path to Vercel Deployment

### Current State
- FastAPI is Vercel-ready (configured in vercel.json)
- Django requires additional setup for Vercel

### Next Steps for Full Vercel Deployment
1. **Build FastAPI** as primary application
2. **Deploy FastAPI** to Vercel (already configured)
3. **Consider Django migration** to Vercel's Python runtime
4. **Add CI/CD** for both implementations
5. **Set up monitoring** and logging
6. **Configure production environment variables**

### Technology Stack Choices
- **Backend**: FastAPI (primary), Django (legacy/alternative)
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: JavaScript framework (to be added)
- **Containerization**: Docker/Kubernetes for scaling
- **Caching**: Redis for seat holds and session management
- **Monitoring**: Application performance monitoring

## Important Notes

### Two Implementations Strategy
This codebase contains **two complete implementations** of the same domain. Consider:
- Which one to develop moving forward
- How to keep them synchronized
- Whether to consolidate into a single implementation
- Migration path for users

### Key Differences to Track
- **Model variations**: Different field types, relationships
- **Authentication systems**: JWT vs. Django auth
- **Database approaches**: SQLAlchemy vs. Django ORM
- **API design**: REST vs. template-based

### Development Recommendations
1. **Start with FastAPI** for new features (cleaner architecture)
2. **Update Django** for consistency where needed
3. **Write integration tests** to ensure both implementations work
4. **Document differences** between implementations
5. **Plan consolidation** for long-term maintainability

## Getting Started

1. **Choose implementation**: FastAPI for new features, Django for legacy/maintenance
2. **Set up environment**: Install dependencies in each directory
3. **Run tests**: Verify both implementations work correctly
4. **Plan feature development**: Decide which implementation to enhance
5. **Consider consolidation**: Long-term strategy for maintenance