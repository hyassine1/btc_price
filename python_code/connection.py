from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os
from binance.client import Client

#script_directory = os.path.dirname(os.path.abspath(__file__))
#env_path = os.path.join(script_directory, '.env')
#load_dotenv(env_path, override=True)

load_dotenv()
api_key    = os.environ.get('API_KEY')
secret_key = os.environ.get('SECRET_KEY')

# Use the environment variables in your code
Client = Client(api_key, secret_key, testnet=True)

HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')
DB = os.environ.get('DB')
USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')


# Create an engine with connection pooling
def get_engine(user, passwd, host, port, db):
    url = f"postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, poolclass=QueuePool, pool_size=50, max_overflow=20)
    return engine


engine   = get_engine(str(USER),str(PASSWORD),str(HOST),str(PORT),str(DB))   

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()