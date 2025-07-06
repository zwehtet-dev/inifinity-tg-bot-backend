from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from migrate import migrate
from models import db
from settings import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

from routes.admin_auth import admin_bp
from routes.home import home_bp
from routes.users import users_bp
from routes.api.auth import auth_bp
from routes.banks import banks_bp
from routes.orders import orders_bp
from routes.api.banks import banks_api
from routes.api.orders import latest_order_bp
from routes.api.settings import settings_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

app.config['SESSION_PERMANENT'] = True  # Make session permanent

app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 1 day in seconds

# Static file serving
app.static_folder = 'static'


# Initialize database (even if no Admin model is used, for future extensibility)
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(admin_bp)
app.register_blueprint(home_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)

app.register_blueprint(banks_bp)
app.register_blueprint(orders_bp)

app.register_blueprint(banks_api)
app.register_blueprint(latest_order_bp)
app.register_blueprint(settings_bp)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
