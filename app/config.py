import os

class Config:
    DATA_DIR = "/data"
    DB_PATH = os.path.join(DATA_DIR, "shop.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DATA_DIR = os.path.join(os.getcwd(), "data")
    DB_PATH = os.path.join(DATA_DIR, "shop.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DB_PATH = ":memory:"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
