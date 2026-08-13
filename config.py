import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolver_ca():
    ruta = os.getenv('MYSQL_SSL_CA')
    if ruta and os.path.isfile(ruta):
        return ruta
    return os.path.join(BASE_DIR, 'app', 'static', 'ssl', 'ca.pem')


class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_PORT = os.getenv('MYSQL_PORT', 3306)
    MYSQL_DB = os.getenv('MYSQL_DB', 'task_manager')
    MYSQL_SSL_CA = _resolver_ca()
    SECRET_KEY = os.getenv('SECRET_KEY', 'default')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_app_password')