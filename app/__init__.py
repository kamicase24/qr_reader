from flask import Flask
from app.extensions import init_extensions
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    # init_extensions(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app