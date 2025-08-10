#!/usr/bin/env python3
"""
Donizo Material Scraper
A web scraper for extracting renovation material pricing data from French suppliers.
"""

import json
import time
import logging
import yaml
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Data class for product information."""
    product_name: str
    category: str
    price: float
    currency: str
    product_url: str
    supplier: str
    timestamp: str
    brand: Optional[str] = None
    measurement_unit: Optional[str] = None
    pack_size: Optional[str] = None
    image_url: Optional[str] = None
    availability: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None


class BaseScraper:
    """Base class for all scrapers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({'User-Agent': self.ua.random})
        
    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content with retry logic."""
        for attempt in range(self.config['scraping']['max_retries']):
            try:
                response = self.session.get(
                    url, 
                    timeout=self.config['scraping']['timeout']
                )
                response.raise_for_status()
                time.sleep(self.config['scraping']['delay_between_requests'])
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.config['scraping']['max_retries'] - 1:
                    logger.error(f"Failed to fetch {url} after {self.config['scraping']['max_retries']} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def _extract_price(self, price_text: str) -> tuple[float, str]:
        """Extract price and currency from text."""
        if not price_text:
            return 0.0, "EUR"
        
        # Remove common price formatting
        price_text = re.sub(r'[^\d,.]', '', price_text)
        price_text = price_text.replace(',', '.')
        
        try:
            price = float(price_text)
            return price, "EUR"  # Default to EUR for French sites
        except ValueError:
            return 0.0, "EUR"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())


class LeroyMerlinScraper(BaseScraper):
    """Scraper for Leroy Merlin website."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config['suppliers']['leroy_merlin']['base_url']
        self.categories = config['suppliers']['leroy_merlin']['categories']
    
    def scrape_category(self, category: str) -> List[Product]:
        """Scrape products from a specific category."""
        products = []
        category_config = self.categories.get(category)
        
        if not category_config:
            logger.error(f"Category {category} not found in configuration")
            return products
        
        url = urljoin(self.base_url, category_config['url_path'])
        logger.info(f"Scraping {category} from {url}")
        
        soup = self._get_page(url)
        if not soup:
            return products
        
        # Find product containers
        product_containers = soup.find_all('div', class_=re.compile(r'product-card|product-item'))
        
        for container in product_containers[:self.config['scraping']['max_products_per_category']]:
            try:
                product = self._extract_product_info(container, category)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error extracting product: {e}")
                continue
        
        return products
    
    def _extract_product_info(self, container, category: str) -> Optional[Product]:
        """Extract product information from a container."""
        try:
            # Product name
            name_elem = container.find('h3') or container.find('h2') or container.find(class_=re.compile(r'title|name'))
            product_name = self._clean_text(name_elem.get_text()) if name_elem else "Unknown Product"
            
            # Product URL
            link_elem = container.find('a')
            product_url = urljoin(self.base_url, link_elem.get('href')) if link_elem else ""
            
            # Price
            price_elem = container.find(class_=re.compile(r'price|prix'))
            price_text = self._clean_text(price_elem.get_text()) if price_elem else "0"
            price, currency = self._extract_price(price_text)
            
            # Brand
            brand_elem = container.find(class_=re.compile(r'brand|marque'))
            brand = self._clean_text(brand_elem.get_text()) if brand_elem else None
            
            # Image URL
            img_elem = container.find('img')
            image_url = urljoin(self.base_url, img_elem.get('src')) if img_elem else None
            
            return Product(
                product_name=product_name,
                category=category,
                price=price,
                currency=currency,
                product_url=product_url,
                supplier="Leroy Merlin",
                timestamp=datetime.now().isoformat(),
                brand=brand,
                image_url=image_url
            )
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return None


class CastoramaScraper(BaseScraper):
    """Scraper for Castorama website."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config['suppliers']['castorama']['base_url']
        self.categories = config['suppliers']['castorama']['categories']
    
    def scrape_category(self, category: str) -> List[Product]:
        """Scrape products from a specific category."""
        products = []
        category_config = self.categories.get(category)
        
        if not category_config:
            logger.error(f"Category {category} not found in configuration")
            return products
        
        url = urljoin(self.base_url, category_config['url_path'])
        logger.info(f"Scraping {category} from {url}")
        
        soup = self._get_page(url)
        if not soup:
            return products
        
        # Find product containers
        product_containers = soup.find_all('div', class_=re.compile(r'product-card|product-item|product'))
        
        for container in product_containers[:self.config['scraping']['max_products_per_category']]:
            try:
                product = self._extract_product_info(container, category)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error extracting product: {e}")
                continue
        
        return products
    
    def _extract_product_info(self, container, category: str) -> Optional[Product]:
        """Extract product information from a container."""
        try:
            # Product name
            name_elem = container.find('h3') or container.find('h2') or container.find(class_=re.compile(r'title|name'))
            product_name = self._clean_text(name_elem.get_text()) if name_elem else "Unknown Product"
            
            # Product URL
            link_elem = container.find('a')
            product_url = urljoin(self.base_url, link_elem.get('href')) if link_elem else ""
            
            # Price
            price_elem = container.find(class_=re.compile(r'price|prix'))
            price_text = self._clean_text(price_elem.get_text()) if price_elem else "0"
            price, currency = self._extract_price(price_text)
            
            # Brand
            brand_elem = container.find(class_=re.compile(r'brand|marque'))
            brand = self._clean_text(brand_elem.get_text()) if brand_elem else None
            
            # Image URL
            img_elem = container.find('img')
            image_url = urljoin(self.base_url, img_elem.get('src')) if img_elem else None
            
            return Product(
                product_name=product_name,
                category=category,
                price=price,
                currency=currency,
                product_url=product_url,
                supplier="Castorama",
                timestamp=datetime.now().isoformat(),
                brand=brand,
                image_url=image_url
            )
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return None


class MaterialScraper:
    """Main scraper class that orchestrates scraping from multiple suppliers."""
    
    def __init__(self, config_path: str = "config/scraper_config.yaml"):
        """Initialize the scraper with configuration."""
        self.config = self._load_config(config_path)
        self.scrapers = {
            'leroy_merlin': LeroyMerlinScraper(self.config),
            'castorama': CastoramaScraper(self.config)
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def scrape_all(self, suppliers: List[str] = None, categories: List[str] = None) -> List[Product]:
        """Scrape products from all specified suppliers and categories."""
        if suppliers is None:
            suppliers = list(self.scrapers.keys())
        
        if categories is None:
            categories = ['tiles', 'sinks', 'toilets', 'paint', 'vanities', 'showers']
        
        all_products = []
        
        for supplier in suppliers:
            if supplier not in self.scrapers:
                logger.warning(f"Supplier {supplier} not found")
                continue
            
            scraper = self.scrapers[supplier]
            logger.info(f"Starting scraping for {supplier}")
            
            for category in categories:
                try:
                    products = scraper.scrape_category(category)
                    all_products.extend(products)
                    logger.info(f"Scraped {len(products)} products from {supplier} - {category}")
                except Exception as e:
                    logger.error(f"Error scraping {category} from {supplier}: {e}")
                    continue
        
        return all_products
    
    def save_to_json(self, products: List[Product], output_path: str = "data/materials.json"):
        """Save products to JSON file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            products_data = [asdict(product) for product in products]
            
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(products_data, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(products)} products to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            raise
    
    def get_api_response(self, category: str = None) -> Dict[str, Any]:
        """Simulate API response for a specific category."""
        products = self.scrape_all(categories=[category] if category else None)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "count": len(products),
            "products": [asdict(product) for product in products]
        }


def main():
    """Main function to run the scraper."""
    try:
        scraper = MaterialScraper()
        
        # Scrape all categories from all suppliers
        products = scraper.scrape_all()
        
        # Save to JSON
        scraper.save_to_json(products)
        
        logger.info(f"Scraping completed. Total products: {len(products)}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    import os
    main()
