import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database settings
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_HOST = os.getenv('DB_HOST')
DB_URL = os.getenv('DB_URL')

# Telegram Bot Token
TOKEN = os.getenv('TOKEN')