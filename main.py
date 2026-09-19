from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from pwdlib import PasswordHash


app = FastAPI()


# -------------------------
# DATABASE
# -------------------------

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase):
    pass


# -------------------------
# USER / MEMBER TABLE
# -------------------------

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(String)


# Create the table
Base.metadata.create_all(engine)


# -------------------------
# PASSWORD HASHING
# -------------------------

password_hash = PasswordHash.recommended()


# -------------------------
# REQUEST SCHEMA
# -------------------------

class RegisterRequest(BaseModel):
    username: str
    password: str


# -------------------------
# REGISTER MEMBER
# -------------------------

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_member(data: RegisterRequest):

    with Session(engine) as session:

        # Check whether username already exists
        existing_member = session.query(Member).filter(
            Member.username == data.username
        ).first()

        if existing_member:
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )

        # Hash the password
        hashed_password = password_hash.hash(data.password)

        # Create member
        member = Member(
            username=data.username,
            password_hash=hashed_password
        )

        # Save to database
        session.add(member)
        session.commit()
        session.refresh(member)

        return {
            "message": "Member registered successfully",
            "username": member.username
        }