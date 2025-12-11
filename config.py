import os
from datetime import timedelta
import pytz

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/bill_database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Indian Standard Time (IST) timezone
    IST_TIMEZONE = pytz.timezone('Asia/Kolkata')
