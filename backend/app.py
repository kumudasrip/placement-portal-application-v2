from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

cors = CORS()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '24f3000060'  

    cors.init_app(app)
    db.init_app(app)

    from .routes import init_app
    init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)