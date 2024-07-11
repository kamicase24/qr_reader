import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(BASE_PATH+'/compose/.env')


class Config:
    SECRET_KEY= os.getenv('SECRET_KEY')
    ODOO_URL = os.getenv('ODOO_URL')
    ODOO_DB = os.getenv('ODOO_DB')
    ODOO_USER = os.getenv('ODOO_USER')
    ODOO_KEY = os.getenv('ODOO_KEY')


    # DB_USER = os.getenv('DB_USER')
    # DB_PASSWORD = os.getenv('DB_PASSWORD')
    # DB_HOST = os.getenv('DB_HOST')
    # DB_PORT = int(os.getenv('DB_PORT'))
    # DATABASE= os.getenv('DATABASE')
    # SQLALCHEMY_DATABASE_URI=f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}'
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
