from datetime import timedelta
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    DB_HOST = os.environ["DB_HOST"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = quote_plus(os.environ["DB_PASSWORD"])
    ALUMNI_DB = os.environ["ALUMNI_DB_NAME"]
    AUTH_DB = os.environ["AUTH_DB_NAME"]
    
    ALUMNI_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{ALUMNI_DB}"
    )
    
    AUTH_DB_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{AUTH_DB}"
    )
    
    SQLALCHEMY_BINDS = {
        "auth": AUTH_DB_URI,
        "alumni": ALUMNI_DATABASE_URI,
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": {
            "ssl": {
                "check_hostname": False
            }
        }
    }
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # INACTIVITY TIMER
    PERMANENT_SESSION_LIFETIME = timedelta(hours=.5)

    # Set this to True in production when the app uses HTTPS.
    SESSION_COOKIE_SECURE = False