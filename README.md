# Student Management API

A minimal FastAPI application for managing students with JWT authentication.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `POST /signup` - Register new user
- `POST /login` - Login and get token
- `GET /students/` - List all students (protected)
- `POST /students/` - Create student (protected)
- `GET /students/{id}` - Get student by ID (protected)
- `PUT /students/{id}` - Update student (protected)
- `DELETE /students/{id}` - Delete student (protected)

## Authentication

Use the token from `/login` in the Authorization header:
```
Authorization: Bearer <your-token>
```
