import os
import psycopg2
import logging
from settings.config import DB_URL

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')
logger = logging.getLogger(__name__)

def connect_to_db():
    """Connects to the PostgreSQL database and returns the connection object."""
    try:
        connection = psycopg2.connect(DB_URL)
        return connection
    except (Exception, psycopg2.Error) as error:
        logger.error("Error connecting to database: %s", error)
        return None