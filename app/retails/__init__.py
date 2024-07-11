from flask import Blueprint

bp = Blueprint('retails', __name__)

from app.retails import routes
