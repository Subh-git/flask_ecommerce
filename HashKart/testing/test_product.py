import unittest
import json
from app import app, db
from app.models import Product

class TestProductRoutes(unittest.TestCase):
    
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
    
    # Test GET /products route
    def test_get_products(self):
        # Insert test products into the database
        product1 = Product(name='Product 1', description='Description 1', price=10.99, quantity=100, category='Category 1', rating=4.5)
        product2 = Product(name='Product 2', description='Description 2', price=15.99, quantity=50, category='Category 2', rating=3.8)
        with app.app_context():
            db.session.add(product1)
            db.session.add(product2)
            db.session.commit()
        
        # Perform a GET request to /products
        response = self.client.get('/products')
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Product 1')
        self.assertEqual(data[1]['name'], 'Product 2')
    
    # Test POST /products route
    def test_add_product(self):
        # Create a test product data
        product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 20.99,
            'quantity': 200,
            'category': 'Test Category',
            'rating': 4.0
        }
        
        # Perform a POST request to /products with the test data
        response = self.client.post('/products', json=product_data)
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Product added successfully')
        
        # Check if the product is inserted into the database
        with app.app_context():
            product = Product.query.filter_by(name='Test Product').first()
            self.assertIsNotNone(product)
            self.assertEqual(product.description, 'Test Description')
            self.assertEqual(product.price, 20.99)
            self.assertEqual(product.quantity, 200)
            self.assertEqual(product.category, 'Test Category')
            self.assertEqual(product.rating, 4.0)
    
    # Test GET /products/<product_id> route
    def test_get_product(self):
        # Insert a test product into the database
        product = Product(name='Test Product', description='Test Description', price=20.99, quantity=200, category='Test Category', rating=4.0)
        with app.app_context():
            db.session.add(product)
            db.session.commit()
        
        # Perform a GET request to /products/<product_id>
        response = self.client.get(f'/products/{product.id}')
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['price'], 20.99)
        self.assertEqual(data['quantity'], 200)
        self.assertEqual(data['category'], 'Test Category')
        self.assertEqual(data['rating'], 4.0)
    
    # Test DELETE /products/<product_id> route
    def test_delete_product(self):
        # Insert a test product into the database
        product = Product(name='Test Product', description='Test Description', price=20.99, quantity=200, category='Test Category', rating=4.0)
        with app.app_context():
            db.session.add(product)
            db.session.commit()
        
        # Perform a DELETE request to /products/<product_id>
        response = self.client.delete(f'/products/{product.id}')
        
        # Check the response status code and data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode('utf-8'))['message'], 'Product deleted successfully')
        
        # Check if the product is deleted from the database
        with app.app_context():
            product = Product.query.filter_by(name='Test Product').first()
            self.assertIsNone(product)

if __name__ == '__main__':
    unittest.main()
