import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.auth.routes import auth_bp
from app.product.routes import product_bp
from app.cart.routes import cart_bp
from app.order.routes import order_bp
from app.discount.routes import discount_bp

app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

if not app.debug:
    file_handler = RotatingFileHandler('hashkart.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('HashKart startup')


@app.route('/', methods=['GET'])
def welcome():
    return "Welcome to HashKart!", 200

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(product_bp, url_prefix='/products')
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(order_bp, url_prefix='/orders')
app.register_blueprint(discount_bp, url_prefix='/discounts')

if __name__ == "__main__":
    print("Server is running")
    app.run(host='0.0.0.0', threaded=True, debug=True)
