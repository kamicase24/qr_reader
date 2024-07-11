from flask import render_template
from app.retails import bp
from app.extensions import Base, db
from sqlalchemy import func, case
from sqlalchemy.orm import Session



@bp.route('/')
def index():
    return render_template('retails/index.html')

