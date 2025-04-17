import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///threat_intel.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database with app
db.init_app(app)

# Initialize API keys from environment variables
app.config["VIRUSTOTAL_API_KEY"] = os.environ.get("VIRUSTOTAL_API_KEY", "")
app.config["ABUSEIPDB_API_KEY"] = os.environ.get("ABUSEIPDB_API_KEY", "")
app.config["ALIENVAULT_API_KEY"] = os.environ.get("ALIENVAULT_API_KEY", "")
app.config["SHODAN_API_KEY"] = os.environ.get("SHODAN_API_KEY", "")

with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    db.create_all()
