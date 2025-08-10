#!/usr/bin/env python3
"""
Demo script for the Donizo Material Scraper
This script demonstrates the basic functionality of the scraper.
"""

import json
import sys
from scraper import MaterialScraper

def main():
    """Demo the scraper functionality."""
    print("Donizo Material Scraper Demo")
    print("=" * 50)
    
    try:
        # Initialize the scraper
        print("Initializing scraper...")
        scraper = MaterialScraper()
        print("Scraper initialized successfully!")
        
        # Show available categories
        print("\nAvailable categories:")
        categories = ['tiles', 'sinks', 'toilets', 'paint', 'vanities', 'showers']
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")
        
        # Show available suppliers
        print("\nAvailable suppliers:")
        suppliers = ['leroy_merlin', 'castorama']
        for i, supplier in enumerate(suppliers, 1):
            print(f"  {i}. {supplier}")
        
        # Demo API response format
        print("\nDemo API response format:")
        print("   GET /materials/tiles")
        
        # Note: In a real demo, this would actually scrape data
        # For demo purposes, we'll show the structure
        demo_response = {
            "status": "success",
            "timestamp": "2023-12-01T10:00:00",
            "category": "tiles",
            "count": 0,  # Would be actual count in real scraping
            "products": []
        }
        
        print(f"   Response: {json.dumps(demo_response, indent=2)}")
        
        # Show sample data structure
        print("\nSample product data structure:")
        sample_product = {
            "product_name": "Carrelage mural blanc brillant 20x20 cm",
            "category": "tiles",
            "price": 12.99,
            "currency": "EUR",
            "product_url": "https://www.leroymerlin.fr/carrelage-mural-blanc-brillant-20x20-cm",
            "supplier": "Leroy Merlin",
            "timestamp": "2023-12-01T10:00:00",
            "brand": "Leroy Merlin",
            "measurement_unit": "m²",
            "pack_size": "1m²"
        }
        
        print(json.dumps(sample_product, indent=2))
        
        # Show configuration
        print("\nCurrent configuration:")
        config = scraper.config
        print(f"   Max products per category: {config['scraping']['max_products_per_category']}")
        print(f"   Delay between requests: {config['scraping']['delay_between_requests']}s")
        print(f"   Max retries: {config['scraping']['max_retries']}")
        print(f"   Output format: {config['output']['format']}")
        
        print("\nTo run actual scraping:")
        print("   python scraper.py")
        print("\nTo start the API server:")
        print("   python api_server.py")
        print("\nTo run tests:")
        print("   pytest tests/")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
