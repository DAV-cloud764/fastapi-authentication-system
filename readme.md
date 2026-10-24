# FastAPI Authentication System

A REST API for member registration, login, JWT authentication, and protected resource access, built with FastAPI and PostgreSQL.

## Tech Stack

- **Python** — Backend
- **FastAPI** — REST API
- **PostgreSQL** — Database
- **SQLAlchemy** — ORM
- **Pydantic** — Data validation
- **pwdlib + Argon2** — Password hashing
- **PyJWT** — JWT authentication
- **Psycopg 3** — PostgreSQL driver

## Features

- Member registration
- Password hashing and verification
- Duplicate username validation
- Member login
- JWT access-token generation
- Protected member profile endpoint
- Member role field
- PostgreSQL database integration

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API home |
| GET | `/about` | API information |
| POST | `/auth/register` | Register a member |
| POST | `/auth/login` | Authenticate and generate JWT |
| GET | `/members/me` | Retrieve authenticated member profile |

## Setup

Clone the repository:

```bash
git clone https://github.com/DAV-cloud764/fastapi-authentication-system.git
cd fastapi-authentication-system
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install "fastapi[standard]" sqlalchemy "psycopg" "pwdlib[argon2]" pyjwt python-dotenv
```

Configure PostgreSQL connection details and JWT settings in a `.env` file.

Start the server:

```bash
python -m uvicorn main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

## Development Status

The core registration, login, JWT authentication, and protected profile features are implemented. Role-based authorization and further improvements are planned.

## Repository

[GitHub — FastAPI Authentication System](https://github.com/DAV-cloud764/fastapi-authentication-system)
