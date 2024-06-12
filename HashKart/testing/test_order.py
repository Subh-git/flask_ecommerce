import unittest
import json
from app import app, db
from app.models import Order, Product, Cart, User
from datetime import datetime

class TestOrderRoutes(unittest.TestCase):
    
    # Set up the test environment
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
    
    # Tear down the test environment
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    # Helper function to create a test user and products
    def create_test_data(self):
        # Create a test user
        user = User(username='test_user', email='test@example.com', password_hash='test_password')
        db.session.add(user)
        
        # Create test products
        product1 = Product(name='Product 1', description='Test Product 1', price=10.0, quantity=100, category='Category 1', rating=4.5)
        product2 = Product(name='Product 2', description='Test Product 2', price=20.0, quantity=50, category='Category 2', rating=4.0)
        db.session.add(product1)
        db.session.add(product2)
        
        # Add products to cart
        cart_item1 = Cart(user_id=user.id, product_id=product1.id, quantity=2)
        cart_item2 = Cart(user_id=user.id, product_id=product2.id, quantity=1)
        db.session.add(cart_item1)
        db.session.add(cart_item2)
        
        db.session.commit()
    
    # Test POST /order route
    def test_create_order(self):
        # Create test data
        self.create_test_data()
        
        # Perform a POST request to /order
        response = self.client.post('/order', json={}, headers={'Authorization': 'Bearer test_token'})
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Order created successfully')
    
    # Test POST /order/payment route
    def test_process_payment(self):
        # Create test data
        self.create_test_data()
        
        # Create a test order
        order = Order(user_id=1, total_amount=50.0, status='Pending')
        db.session.add(order)
        db.session.commit()
        
        # Perform a POST request to /order/payment with test data
        payment_data = {'order_id': order.id, 'payment_method': 'Credit Card'}
        response = self.client.post('/order/payment', json=payment_data, headers={'Authorization': 'Bearer test_token'})
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Payment processed successfully')

if __name__ == '__main__':
    unittest.main()
