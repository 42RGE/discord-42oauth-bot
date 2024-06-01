from flask_sqlalchemy import SQLAlchemy
from zenora import APIClient
from config import TOKEN, CLIENT_SECRET

db = SQLAlchemy()
client = APIClient(TOKEN, client_secret=CLIENT_SECRET)
