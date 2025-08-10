#!/usr/bin/env python3
"""
Donizo Material Scraper API Server
A simple Flask API to serve scraped material data.
"""

from flask import Flask, jsonify, request
from scraper import MaterialScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
scraper = None

def initialize_scraper():
    """Initialize the scraper on first request."""
    global scraper
    if scraper is None:
        try:
            scraper = MaterialScraper()
            logger.info("Scraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise
    return scraper

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Donizo Material Scraper API"
    })

@app.route('/materials', methods=['GET'])
def get_all_materials():
    """Get all materials from all categories."""
    try:
        scraper_instance = initialize_scraper()
        category = request.args.get('category')
        supplier = request.args.get('supplier')
        
        if category:
            return get_materials_by_category(category)
        elif supplier:
            return get_materials_by_supplier(supplier)
        else:
            # Return cached data if available, otherwise scrape
            response = scraper_instance.get_api_response()
            return jsonify(response)
            
    except Exception as e:
        logger.error(f"Error in get_all_materials: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/materials/<category>', methods=['GET'])
def get_materials_by_category(category):
    """Get materials by specific category."""
    try:
        scraper_instance = initialize_scraper()
        response = scraper_instance.get_api_response(category)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting materials for category {category}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/materials/supplier/<supplier>', methods=['GET'])
def get_materials_by_supplier(supplier):
    """Get materials by specific supplier."""
    try:
        scraper_instance = initialize_scraper()
        suppliers = [supplier] if supplier in ['leroy_merlin', 'castorama'] else []
        products = scraper_instance.scrape_all(suppliers=suppliers)
        
        response = {
            "status": "success",
            "timestamp": scraper_instance.get_api_response()["timestamp"],
            "supplier": supplier,
            "count": len(products),
            "products": [scraper.Product.__dict__ for product in products]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting materials for supplier {supplier}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available categories."""
    categories = ['tiles', 'sinks', 'toilets', 'paint', 'vanities', 'showers']
    return jsonify({
        "status": "success",
        "categories": categories
    })

@app.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get available suppliers."""
    suppliers = ['leroy_merlin', 'castorama']
    return jsonify({
        "status": "success",
        "suppliers": suppliers
    })

@app.route('/scrape', methods=['POST'])
def trigger_scrape():
    """Trigger a new scraping job."""
    try:
        scraper_instance = initialize_scraper()
        data = request.get_json() or {}
        suppliers = data.get('suppliers')
        categories = data.get('categories')
        
        products = scraper_instance.scrape_all(suppliers=suppliers, categories=categories)
        scraper_instance.save_to_json(products)
        
        return jsonify({
            "status": "success",
            "message": f"Scraped {len(products)} products",
            "count": len(products)
        })
        
    except Exception as e:
        logger.error(f"Error in trigger_scrape: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
