import os
from datetime import timedelta

class Config:
    """Base configuration with common settings."""
    
    # Secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # Change to a secure random string

    # Set the URI for the SQLite database (you can change this path if needed)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources
    SQLALCHEMY_ECHO = False  # Set to True for debugging database queries (optional)

    # Caching configuration using Redis
    CACHE_TYPE = 'RedisCache'
    CACHE_DEFAULT_TIMEOUT = 300  # Cache expiry time in seconds
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    
    # Email configurations for sending email reminders or activity reports
    MAIL_SERVER = 'smtp.gmail.com'  # Example using Gmail
    MAIL_PORT = 587  # Standard SMTP port
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Email address to send from
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # App password (not your real password)
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@example.com')

    # Configuration for JWT Token expiration (if using JWT for authentication)
    JWT_EXPIRATION_DELTA = timedelta(days=7)  # Default expiration of 7 days for JWTs
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')  # Change to a secure string

    # Flask-Login / Flask-Security settings (if you're using these for login)
    LOGIN_MANAGER_LOGIN_VIEW = 'auth.login'
    LOGIN_MANAGER_SESSION_PROTECTION = 'strong'

    # Path to store user-uploaded documents (for professional verification)
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}  # Allowed file extensions for uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size: 16 MB

    # Scheduled Jobs Settings
    REMINDER_TIME = os.getenv('REMINDER_TIME', '18:00')  # Set reminder time (18:00 for 6 PM)
    MONTHLY_REPORT_DAY = 1  # Day of the month to generate monthly activity reports


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""
    
    DEBUG = True
    FLASK_ENV = 'development'
    TESTING = True  # Enable testing mode (good for unit tests)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db_dev.sqlite3')  # Use a dev database
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  # Use local Redis
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')  # Celery local setup


class ProductionConfig(Config):
    """Production configuration with optimized settings for production."""
    
    DEBUG = False
    FLASK_ENV = 'production'
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')  # Production database URL
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  # Production Redis setup
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')  # Celery production setup


class TestingConfig(Config):
    """Testing configuration for unit tests and testing environments."""
    
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db_test.sqlite3')  # Test database
    CACHE_TYPE = 'null'  # Disable caching in the testing environment


# Set the active configuration class based on the environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
