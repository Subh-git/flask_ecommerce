import unittest
import json
from app import app, db
from app.models import Cart, Product

class TestCartRoutes(unittest.TestCase):
    
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
    
    # Test GET /cart route
    def test_get_cart(self):
        # Insert a test cart item into the database
        cart_item = Cart(user_id=1, product_id=1, quantity=2)
        with app.app_context():
            db.session.add(cart_item)
            db.session.commit()
        
        # Perform a GET request to /cart
        response = self.client.get('/cart')
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['product_id'], 1)
        self.assertEqual(data[0]['quantity'], 2)
    
    # Test POST /cart route
    def test_add_to_cart(self):
        # Insert a test product into the database
        product = Product(name='Test Product', description='Test Description', price=20.99, quantity=200, category='Test Category', rating=4.0)
        with app.app_context():
            db.session.add(product)
            db.session.commit()
        
        # Create a test cart item data
        cart_item_data = {'product_id': product.id, 'quantity': 2}
        
        # Perform a POST request to /cart with the test data
        response = self.client.post('/cart', json=cart_item_data)
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Item added to cart successfully')
        
        # Check if the cart item is inserted into the database
        with app.app_context():
            cart_item = Cart.query.first()
            self.assertIsNotNone(cart_item)
            self.assertEqual(cart_item.product_id, product.id)
            self.assertEqual(cart_item.quantity, 2)
    
    # Test DELETE /cart/<product_id> route
    def test_remove_from_cart(self):
        # Insert a test cart item into the database
        cart_item = Cart(user_id=1, product_id=1, quantity=2)
        with app.app_context():
            db.session.add(cart_item)
            db.session.commit()
        
        # Perform a DELETE request to /cart/<product_id>
        response = self.client.delete('/cart/1')
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Item removed from cart successfully')
        
        # Check if the cart item is deleted from the database
        with app.app_context():
            cart_item = Cart.query.first()
            self.assertIsNone(cart_item)

if __name__ == '__main__':
    unittest.main()
