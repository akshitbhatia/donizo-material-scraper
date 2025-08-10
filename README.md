# Donizo Material Scraper

A Python-based web scraper for extracting renovation material pricing data from major French suppliers. This project is designed to provide structured, developer-friendly pricing data for Donizo's pricing engine.

## Objective

Scrape real renovation material pricing data from major French suppliers and structure it in a developer- and product-friendly format for Donizo's pricing engine.

## Project Structure

```
/donizo-material-scraper/
├── scraper.py              # Main scraper module
├── api_server.py           # Flask API server
├── config/
│   └── scraper_config.yaml # Configuration file
├── data/
│   └── materials.json      # Sample output data
├── tests/
│   └── test_scraper.py     # Test suite
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

### Core Functionality
- **Multi-supplier scraping**: Support for Leroy Merlin and Castorama
- **Multiple categories**: Tiles, sinks, toilets, paint, vanities, showers
- **Structured data output**: JSON format with comprehensive product information
- **Configurable scraping**: YAML-based configuration for easy customization
- **Error handling**: Robust retry logic and error recovery
- **Rate limiting**: Built-in delays to respect website policies

### Bonus Features (Elite Level)
- **API simulation**: RESTful API endpoints for data access
- **Modular configuration**: YAML-based config for easy supplier/category management
- **Timestamped data**: Version tracking for price changes over time
- **Vector DB ready**: Structured output optimized for future vector database integration
- **Multi-supplier comparison**: Extract and compare prices across suppliers
- **Availability tracking**: Handle out-of-stock flags and availability logic

## Requirements

### Python Dependencies
- Python 3.8+
- See `requirements.txt` for complete list

### System Requirements
- Chrome/Chromium browser (for Selenium-based scraping)
- Internet connection for web scraping

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd donizo-material-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -c "import scraper; print('Installation successful!')"
   ```

## Usage

### Basic Usage

1. **Run the scraper**
   ```bash
   python scraper.py
   ```

2. **Check the output**
   ```bash
   cat data/materials.json
   ```

### Advanced Usage

#### Scrape specific categories
```python
from scraper import MaterialScraper

scraper = MaterialScraper()
products = scraper.scrape_all(categories=['tiles', 'paint'])
scraper.save_to_json(products, 'data/tiles_and_paint.json')
```

#### Scrape specific suppliers
```python
products = scraper.scrape_all(suppliers=['leroy_merlin'])
```

#### Get API response format
```python
response = scraper.get_api_response('tiles')
print(f"Found {response['count']} tile products")
```

### API Server

1. **Start the API server**
   ```bash
   python api_server.py
   ```

2. **Access endpoints**
   ```bash
   # Health check
   curl http://localhost:5000/health
   
   # Get all materials
   curl http://localhost:5000/materials
   
   # Get materials by category
   curl http://localhost:5000/materials/tiles
   
   # Get materials by supplier
   curl http://localhost:5000/materials/supplier/leroy_merlin
   
   # Trigger new scraping job
   curl -X POST http://localhost:5000/scrape \
     -H "Content-Type: application/json" \
     -d '{"categories": ["tiles", "paint"]}'
   ```

## Output Format

### JSON Structure
Each product is structured as follows:

```json
{
  "product_name": "Carrelage mural blanc brillant 20x20 cm",
  "category": "tiles",
  "price": 12.99,
  "currency": "EUR",
  "product_url": "https://www.leroymerlin.fr/carrelage-mural-blanc-brillant-20x20-cm",
  "supplier": "Leroy Merlin",
  "timestamp": "2023-12-01T10:00:00",
  "brand": "Leroy Merlin",
  "measurement_unit": "m²",
  "pack_size": "1m²",
  "image_url": "https://www.leroymerlin.fr/images/carrelage-blanc.jpg",
  "availability": "En stock",
  "description": "Carrelage mural blanc brillant pour salle de bain et cuisine",
  "sku": "LM-CAR-001"
}
```

### Required Fields
- `product_name`: Name of the product
- `category`: Product category (tiles, sinks, toilets, paint, vanities, showers)
- `price`: Product price as float
- `currency`: Currency code (EUR)
- `product_url`: Direct link to the product page
- `supplier`: Supplier name (Leroy Merlin, Castorama)
- `timestamp`: ISO timestamp of when data was scraped

### Optional Fields
- `brand`: Product brand name
- `measurement_unit`: Unit of measurement (m², L, unité, etc.)
- `pack_size`: Package size or quantity
- `image_url`: URL to product image
- `availability`: Stock availability status
- `description`: Product description
- `sku`: Stock keeping unit

## Configuration

### Scraper Configuration (`config/scraper_config.yaml`)

The configuration file allows you to:

- **Define suppliers**: Add new suppliers with their base URLs and category mappings
- **Configure scraping behavior**: Set delays, timeouts, retry limits
- **Customize output**: Choose format, include timestamps, enable compression
- **Browser settings**: Configure Selenium browser options

### Key Configuration Sections

```yaml
# Supplier definitions
suppliers:
  leroy_merlin:
    name: "Leroy Merlin"
    base_url: "https://www.leroymerlin.fr"
    categories:
      tiles:
        url_path: "/carrelage-faience-mosaique"

# Scraping behavior
scraping:
  max_products_per_category: 50
  delay_between_requests: 2
  timeout: 30
  max_retries: 3

# Output settings
output:
  format: "json"
  include_timestamp: true
```

## Testing

### Run all tests
```bash
pytest tests/
```

### Run specific test categories
```bash
pytest tests/test_scraper.py::TestProduct
pytest tests/test_scraper.py::TestMaterialScraper
```

### Test coverage
```bash
pytest --cov=scraper tests/
```

## Data Assumptions & Transformations

### Price Extraction
- Prices are extracted from text using regex patterns
- French number formatting (comma as decimal separator) is handled
- Default currency is EUR for French suppliers
- Invalid prices default to 0.0

### Text Cleaning
- Extra whitespace is normalized
- HTML entities are decoded
- Special characters are preserved for French text

### URL Handling
- Relative URLs are converted to absolute URLs
- Invalid URLs are filtered out
- Base URLs are prepended when needed

### Category Mapping
- Categories are standardized across suppliers
- French category names are mapped to English equivalents
- Invalid categories are logged and skipped

## Anti-Bot Handling

### Built-in Protections
- **User-Agent rotation**: Random user agents for each request
- **Request delays**: Configurable delays between requests
- **Retry logic**: Exponential backoff for failed requests
- **Session management**: Persistent sessions with cookies
- **Error handling**: Graceful handling of network issues

### Recommended Practices
- Respect robots.txt files
- Use reasonable delays (2+ seconds between requests)
- Monitor for rate limiting responses
- Implement IP rotation if needed (not included in basic version)

## Pagination & Dynamic Content

### Current Implementation
- Basic pagination support through URL patterns
- Static content scraping using BeautifulSoup
- Product container detection using CSS class patterns

### Future Enhancements
- Selenium-based dynamic content loading
- Infinite scroll handling
- Load-more button automation
- JavaScript-rendered content support

## Auto-Sync Pipeline Proposal

### Monthly Sync Strategy
1. **Scheduled scraping**: Cron job or cloud scheduler
2. **Version control**: Timestamped data files
3. **Change detection**: Compare with previous versions
4. **Notification system**: Alert on significant price changes
5. **Data archiving**: Keep historical data for trend analysis

### Implementation Steps
1. Set up cloud infrastructure (AWS/GCP/Azure)
2. Configure scheduled jobs (Cloud Scheduler, Lambda)
3. Implement change detection algorithm
4. Set up monitoring and alerting
5. Create data archival strategy

## Error Handling

### Common Issues
- **Network timeouts**: Handled with retry logic
- **Invalid HTML**: Graceful parsing with fallbacks
- **Missing data**: Optional fields default to None
- **Rate limiting**: Exponential backoff and delays

### Logging
- Comprehensive logging at INFO level
- Error details captured for debugging
- Progress tracking for long-running scrapes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is created for the Donizo Data Engineer Test Case 2.

## Future Enhancements

- **ManoMano integration**: Add third supplier support
- **Price comparison dashboard**: Web interface for data visualization
- **Machine learning integration**: Price prediction and anomaly detection
- **Real-time monitoring**: Live price tracking
- **Export formats**: CSV, Excel, API endpoints
- **Geographic expansion**: Support for other European markets

---

**Built for Donizo's global pricing engine foundation**