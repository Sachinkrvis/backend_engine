# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import ssl

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SSL context
ssl_context = ssl.create_default_context()

# Neon uses self-signed certs
# ssl_context.check_hostname = False  
# ssl_context.verify_mode = ssl.CERT_NONE

 # Render db
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Render db
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True, 
    connect_args={"ssl": ssl_context}
)

# neon db
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=True,
#     future=True,
#     connect_args={"ssl": ssl_context}  # pass SSL config here
# )

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
