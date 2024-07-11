from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

db = SQLAlchemy()
Base = automap_base()

def init_extensions(app):
    with app.app_context():
        db.init_app(app)
        Base.prepare(db.engine, reflect=True)
    
