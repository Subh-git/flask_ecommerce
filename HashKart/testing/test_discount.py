import unittest
import json
from app import app, db
from app.models import Discount

class TestDiscountRoutes(unittest.TestCase):
    
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
    
    # Test GET /discount route
    def test_get_discounts(self):
        # Insert test discounts into the database
        discount1 = Discount(code='DISCOUNT1', description='Test Discount 1', discount_percent=10, valid_from='2024-01-01', valid_to='2024-12-31')
        discount2 = Discount(code='DISCOUNT2', description='Test Discount 2', discount_percent=20, valid_from='2024-01-01', valid_to='2024-12-31')
        with app.app_context():
            db.session.add(discount1)
            db.session.add(discount2)
            db.session.commit()
        
        # Perform a GET request to /discount
        response = self.client.get('/discount')
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['code'], 'DISCOUNT1')
        self.assertEqual(data[1]['code'], 'DISCOUNT2')
    
    # Test POST /discount/apply route
    def test_apply_discount(self):
        # Insert a test discount into the database
        discount = Discount(code='DISCOUNT1', description='Test Discount', discount_percent=10, valid_from='2024-01-01', valid_to='2024-12-31')
        with app.app_context():
            db.session.add(discount)
            db.session.commit()
        
        # Create a test order data
        order_data = {'order_id': 1, 'code': 'DISCOUNT1'}
        
        # Perform a POST request to /discount/apply with the test data
        response = self.client.post('/discount/apply', json=order_data)
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Discount applied successfully')
    
    # Test POST /discount/apply route with invalid discount code
    def test_apply_invalid_discount(self):
        # Create a test order data with an invalid discount code
        order_data = {'order_id': 1, 'code': 'INVALID'}
        
        # Perform a POST request to /discount/apply with the test data
        response = self.client.post('/discount/apply', json=order_data)
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Invalid or expired discount code')

if __name__ == '__main__':
    unittest.main()
