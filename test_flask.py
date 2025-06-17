#!/usr/bin/env python3
"""
Simple test script to verify Flask installation and basic functionality
"""

try:
    from flask import Flask
    print("✓ Flask imported successfully")
    
    app = Flask(__name__)
    print("✓ Flask app created successfully")
    
    @app.route('/')
    def hello():
        return '<h1>VerdeQR Test Server</h1><p>Flask is working correctly!</p>'
    
    @app.route('/test')
    def test():
        return {'status': 'ok', 'message': 'Test endpoint working'}
    
    if __name__ == '__main__':
        print("Starting test Flask server...")
        print("Visit http://localhost:5000 to see if it's working")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
