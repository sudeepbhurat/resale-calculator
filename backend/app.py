from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import lru_cache
import math
import os
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": [
        "http://localhost:3000",
        "https://resale-calculator.vercel.app",
        "https://resale-calculator-frontend.vercel.app"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

# Cache the depreciation rates
DEPRECIATION_MODELS = {
    "Electronics": [0.70, 0.85, 0.90],  # Year 1: 30% drop, Year 2: 15%, then 10% yearly
    "Cycles": [0.80, 0.90, 0.95],       # Year 1: 20% drop, Year 2: 10%, then 5% yearly
    "Appliances": [0.85, 0.90, 0.95],   # Year 1: 15% drop, Year 2: 10%, then 5% yearly
}

# Cache the condition factors
CONDITION_FACTORS = {
    "new": 1.0,
    "good": 0.9,
    "decent": 0.75,
    "average": 0.6,
    "poor": 0.4
}

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        print(f"{request.method} {request.path} - {duration:.3f}s")
    return response

@lru_cache(maxsize=128)
def get_depreciation_rates(category):
    return DEPRECIATION_MODELS.get(category, [0.80, 0.90, 0.95])

@lru_cache(maxsize=128)
def get_condition_factor(condition):
    return CONDITION_FACTORS.get(condition, 0.9)

@lru_cache(maxsize=128)
def resale_price(original_price, age, category, condition):
    condition_factor = get_condition_factor(condition)
    
    if age <= 0:
        return round(original_price * condition_factor, 2)
    
    depreciation_factors = get_depreciation_rates(category)
    
    if age == 1:
        resale_value = original_price * depreciation_factors[0]
    elif age == 2:
        resale_value = original_price * depreciation_factors[0] * depreciation_factors[1]
    else:
        resale_value = original_price * depreciation_factors[0] * depreciation_factors[1] * (depreciation_factors[2] ** (age - 2))
    
    return round(resale_value * condition_factor, 2)

@app.route('/api/calculate', methods=['POST', 'OPTIONS'])
def calculate_resale():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        original_price = float(data.get('original_price', 0))
        age = int(data.get('age', 0))
        category = data.get('category', 'Electronics')
        condition = data.get('condition', 'good')

        if original_price <= 0 or age < 0:
            return jsonify({'error': 'Invalid price or age'}), 400

        price = resale_price(original_price, age, category, condition)
        return jsonify({
            'resale_price': price,
            'original_price': original_price,
            'age': age,
            'category': category,
            'condition': condition
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/categories', methods=['GET', 'OPTIONS'])
def get_categories():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(list(DEPRECIATION_MODELS.keys()))

@app.route('/api/conditions', methods=['GET', 'OPTIONS'])
def get_conditions():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(list(CONDITION_FACTORS.keys()))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
