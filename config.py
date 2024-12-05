import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456789'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://Benedek:Hype#24Python!@localhost/compare'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
