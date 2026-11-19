import os
import ssl
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD", "")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{USER}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DB_NAME}"

connect_args = {}
if HOST not in ("localhost", "127.0.0.1"):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Função utilitária para abrir/fechar sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()