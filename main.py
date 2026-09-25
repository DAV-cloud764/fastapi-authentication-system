import os

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from pwdlib import PasswordHash

from sqlalchemy import String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from datetime import datetime, timedelta, timezone
import jwt


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="FastAPI Authentication System"
)


# =========================================================
# DATABASE
# =========================================================

engine = create_engine(DATABASE_URL)


# =========================================================
# DATABASE BASE CLASS
# =========================================================

class Base(DeclarativeBase):
    pass


# =========================================================
# MEMBER DATABASE MODEL
# =========================================================

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )


# =========================================================
# CREATE TABLES
# =========================================================

Base.metadata.create_all(engine)


# =========================================================
# PASSWORD HASHING
# =========================================================

password_hash = PasswordHash.recommended()


# =========================================================
# REQUEST SCHEMA
# =========================================================

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str    


# =========================================================
# DATABASE CONNECTION TEST
# =========================================================

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Database connection:", result.scalar())


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")    


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def home():
    return {
        "message": "FastAPI Authentication System"
    }


@app.get("/about")
def about():
    return {
        "message": "Welcome to the About Page!"
    }


# =========================================================
# REGISTER MEMBER
# =========================================================

@app.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED
)
def register_member(data: RegisterRequest):

    with Session(engine) as session:

        # 1. Look for an existing username
        statement = select(Member).where(
            Member.username == data.username
        )

        existing_member = session.scalar(statement)

        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # 2. Hash the password
        hashed_password = password_hash.hash(
            data.password
        )

        # 3. Create a Member object
        member = Member(
            username=data.username,
            password_hash=hashed_password
        )

        # 4. Add the member to the session
        session.add(member)

        # 5. Commit the transaction
        session.commit()

        # 6. Refresh the object
        session.refresh(member)

        return {
            "message": "Member registered successfully",
            "username": member.username
        }



def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )

def create_access_token(
    member_id: int,
    expires_delta: timedelta | None = None
) -> str:

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(member_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/auth/login")
def login_member(data: LoginRequest):

    with Session(engine) as session:

        # 1. Find the member by username
        statement = select(Member).where(
            Member.username == data.username
        )

        member = session.scalar(statement)

        # 2. Make sure the member exists
        if not member:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # 3. Verify the submitted password
        if not verify_password(
            data.password,
            member.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # 4. Authentication succeeded
        access_token = create_access_token(
    member_id=member.id
)

    return Token(
    access_token=access_token,
    token_type="bearer"
)