from flask import Flask

def create_app():
    app = Flask(__name__)

    # Blueprint 등록
    from app.routes import example
    app.register_blueprint(example.bp)

    return app