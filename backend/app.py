from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://your-netlify-domain.netlify.app"]}})

def get_depreciation_rates(category):
    """
    Returns the depreciation rates for a given product category.
    """
    depreciation_models = {
        "Electronics": [0.70, 0.85, 0.90],  # Year 1: 30% drop, Year 2: 15%, then 10% yearly
        "Cycles": [0.80, 0.90, 0.95],       # Year 1: 20% drop, Year 2: 10%, then 5% yearly
        "Appliances": [0.85, 0.90, 0.95],   # Year 1: 15% drop, Year 2: 10%, then 5% yearly
    }
    return depreciation_models.get(category, [0.80, 0.90, 0.95])  # Default rates if category not found

def get_condition_factor(condition):
    """
    Returns a condition factor multiplier based on product condition.
    """
    condition_factors = {
        "new": 1.0,
        "good": 0.9,
        "decent": 0.75,
        "average": 0.6,
        "poor": 0.4
    }
    return condition_factors.get(condition, 0.9)  # Default to 'good' if invalid

def resale_price(original_price, age, category, condition):
    """
    Calculate the resale price of a product using a piecewise depreciation model.
    """
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

@app.route('/api/calculate', methods=['POST'])
def calculate_resale():
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

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = ["Electronics", "Cycles", "Appliances"]
    return jsonify(categories)

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    conditions = ["new", "good", "decent", "average", "poor"]
    return jsonify(conditions)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 