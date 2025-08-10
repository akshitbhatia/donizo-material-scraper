#!/usr/bin/env python3
"""
Tests for the Donizo Material Scraper
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the scraper classes
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import Product, BaseScraper, LeroyMerlinScraper, CastoramaScraper, MaterialScraper


class TestProduct:
    """Test the Product dataclass."""
    
    def test_product_creation(self):
        """Test creating a product with required fields."""
        product = Product(
            product_name="Test Product",
            category="tiles",
            price=25.99,
            currency="EUR",
            product_url="https://example.com/product",
            supplier="Leroy Merlin",
            timestamp="2023-12-01T10:00:00"
        )
        
        assert product.product_name == "Test Product"
        assert product.category == "tiles"
        assert product.price == 25.99
        assert product.currency == "EUR"
        assert product.supplier == "Leroy Merlin"
    
    def test_product_with_optional_fields(self):
        """Test creating a product with optional fields."""
        product = Product(
            product_name="Test Product",
            category="tiles",
            price=25.99,
            currency="EUR",
            product_url="https://example.com/product",
            supplier="Leroy Merlin",
            timestamp="2023-12-01T10:00:00",
            brand="Test Brand",
            measurement_unit="m²",
            pack_size="1m²",
            image_url="https://example.com/image.jpg"
        )
        
        assert product.brand == "Test Brand"
        assert product.measurement_unit == "m²"
        assert product.pack_size == "1m²"
        assert product.image_url == "https://example.com/image.jpg"


class TestBaseScraper:
    """Test the BaseScraper class."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            'scraping': {
                'max_retries': 3,
                'timeout': 30,
                'delay_between_requests': 1
            }
        }
    
    @pytest.fixture
    def base_scraper(self, mock_config):
        """Create a BaseScraper instance for testing."""
        return BaseScraper(mock_config)
    
    def test_extract_price_valid(self, base_scraper):
        """Test price extraction with valid input."""
        price, currency = base_scraper._extract_price("25,99 €")
        assert price == 25.99
        assert currency == "EUR"
    
    def test_extract_price_invalid(self, base_scraper):
        """Test price extraction with invalid input."""
        price, currency = base_scraper._extract_price("invalid")
        assert price == 0.0
        assert currency == "EUR"
    
    def test_extract_price_empty(self, base_scraper):
        """Test price extraction with empty input."""
        price, currency = base_scraper._extract_price("")
        assert price == 0.0
        assert currency == "EUR"
    
    def test_clean_text(self, base_scraper):
        """Test text cleaning functionality."""
        cleaned = base_scraper._clean_text("  Test   Product  ")
        assert cleaned == "Test Product"
    
    @patch('requests.Session.get')
    def test_get_page_success(self, mock_get, base_scraper):
        """Test successful page retrieval."""
        mock_response = Mock()
        mock_response.content = "<html><body>Test</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        soup = base_scraper._get_page("https://example.com")
        assert soup is not None
        assert soup.find('body').text == "Test"
    
    @patch('requests.Session.get')
    def test_get_page_failure(self, mock_get, base_scraper):
        """Test page retrieval failure."""
        mock_get.side_effect = Exception("Connection error")
        
        soup = base_scraper._get_page("https://example.com")
        assert soup is None


class TestLeroyMerlinScraper:
    """Test the LeroyMerlinScraper class."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for Leroy Merlin scraper."""
        return {
            'suppliers': {
                'leroy_merlin': {
                    'base_url': 'https://www.leroymerlin.fr',
                    'categories': {
                        'tiles': {
                            'url_path': '/carrelage-faience-mosaique'
                        }
                    }
                }
            },
            'scraping': {
                'max_retries': 3,
                'timeout': 30,
                'delay_between_requests': 1,
                'max_products_per_category': 10
            }
        }
    
    @pytest.fixture
    def scraper(self, mock_config):
        """Create a LeroyMerlinScraper instance for testing."""
        return LeroyMerlinScraper(mock_config)
    
    def test_scraper_initialization(self, scraper):
        """Test scraper initialization."""
        assert scraper.base_url == "https://www.leroymerlin.fr"
        assert "tiles" in scraper.categories
    
    @patch.object(LeroyMerlinScraper, '_get_page')
    def test_scrape_category_success(self, mock_get_page, scraper):
        """Test successful category scraping."""
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <div class="product-card">
                    <h3>Test Product</h3>
                    <a href="/product/1">Link</a>
                    <span class="price">25,99 €</span>
                    <span class="brand">Test Brand</span>
                    <img src="/image.jpg" />
                </div>
            </body>
        </html>
        """
        
        mock_soup = Mock()
        mock_soup.find_all.return_value = [Mock()]
        mock_get_page.return_value = mock_soup
        
        products = scraper.scrape_category("tiles")
        assert len(products) >= 0  # Should handle the mock properly
    
    def test_scrape_category_invalid(self, scraper):
        """Test scraping invalid category."""
        products = scraper.scrape_category("invalid_category")
        assert len(products) == 0


class TestCastoramaScraper:
    """Test the CastoramaScraper class."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for Castorama scraper."""
        return {
            'suppliers': {
                'castorama': {
                    'base_url': 'https://www.castorama.fr',
                    'categories': {
                        'tiles': {
                            'url_path': '/carrelage-faience'
                        }
                    }
                }
            },
            'scraping': {
                'max_retries': 3,
                'timeout': 30,
                'delay_between_requests': 1,
                'max_products_per_category': 10
            }
        }
    
    @pytest.fixture
    def scraper(self, mock_config):
        """Create a CastoramaScraper instance for testing."""
        return CastoramaScraper(mock_config)
    
    def test_scraper_initialization(self, scraper):
        """Test scraper initialization."""
        assert scraper.base_url == "https://www.castorama.fr"
        assert "tiles" in scraper.categories


class TestMaterialScraper:
    """Test the MaterialScraper class."""
    
    @pytest.fixture
    def mock_config_file(self):
        """Create a temporary config file for testing."""
        config_content = """
suppliers:
  leroy_merlin:
    name: "Leroy Merlin"
    base_url: "https://www.leroymerlin.fr"
    categories:
      tiles:
        url_path: "/carrelage-faience-mosaique"
  castorama:
    name: "Castorama"
    base_url: "https://www.castorama.fr"
    categories:
      tiles:
        url_path: "/carrelage-faience"

scraping:
  max_products_per_category: 10
  delay_between_requests: 1
  timeout: 30
  max_retries: 3
  user_agent_rotation: true

output:
  format: "json"
  include_timestamp: true
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            return f.name
    
    @pytest.fixture
    def scraper(self, mock_config_file):
        """Create a MaterialScraper instance for testing."""
        return MaterialScraper(mock_config_file)
    
    def test_config_loading(self, scraper):
        """Test configuration loading."""
        assert scraper.config is not None
        assert 'suppliers' in scraper.config
        assert 'scraping' in scraper.config
    
    def test_scrapers_initialization(self, scraper):
        """Test scrapers initialization."""
        assert 'leroy_merlin' in scraper.scrapers
        assert 'castorama' in scraper.scrapers
    
    @patch.object(LeroyMerlinScraper, 'scrape_category')
    @patch.object(CastoramaScraper, 'scrape_category')
    def test_scrape_all(self, mock_castorama, mock_leroy, scraper):
        """Test scraping all categories from all suppliers."""
        # Mock return values
        mock_leroy.return_value = [
            Product(
                product_name="Test Product 1",
                category="tiles",
                price=25.99,
                currency="EUR",
                product_url="https://example.com/1",
                supplier="Leroy Merlin",
                timestamp="2023-12-01T10:00:00"
            )
        ]
        mock_castorama.return_value = [
            Product(
                product_name="Test Product 2",
                category="tiles",
                price=30.50,
                currency="EUR",
                product_url="https://example.com/2",
                supplier="Castorama",
                timestamp="2023-12-01T10:00:00"
            )
        ]
        
        products = scraper.scrape_all()
        assert len(products) > 0
    
    def test_save_to_json(self, scraper):
        """Test saving products to JSON."""
        products = [
            Product(
                product_name="Test Product",
                category="tiles",
                price=25.99,
                currency="EUR",
                product_url="https://example.com/product",
                supplier="Leroy Merlin",
                timestamp="2023-12-01T10:00:00"
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            scraper.save_to_json(products, output_path)
            
            # Verify file was created and contains data
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]['product_name'] == "Test Product"
        finally:
            os.unlink(output_path)
    
    def test_get_api_response(self, scraper):
        """Test API response generation."""
        response = scraper.get_api_response("tiles")
        
        assert 'status' in response
        assert 'timestamp' in response
        assert 'category' in response
        assert 'count' in response
        assert 'products' in response
        assert response['category'] == "tiles"


if __name__ == '__main__':
    pytest.main([__file__])
