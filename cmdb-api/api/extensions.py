# -*- coding:utf-8 -*-


from celery import Celery
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from api.lib.secrets.inner import KeyManage
from api.lib.utils import ESHandler
from api.lib.utils import RedisHandler

bcrypt = Bcrypt()
babel = Babel()
login_manager = LoginManager()
db = SQLAlchemy(session_options={"autoflush": False})
migrate = Migrate()
cache = Cache()
celery = Celery()
# Configure CORS to allow requests from frontend
cors = CORS(
    supports_credentials=True,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization", "Access-Token", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
)
rd = RedisHandler()
es = ESHandler()
inner_secrets = KeyManage()
