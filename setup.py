#!/usr/bin/env python3
"""
Setup script for Donizo Material Scraper
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="donizo-material-scraper",
    version="1.0.0",
    author="Donizo Team",
    author_email="team@donizo.com",
    description="A web scraper for extracting renovation material pricing data from French suppliers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/donizo/material-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "donizo-scraper=scraper:main",
            "donizo-api=api_server:app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "data/*.json"],
    },
    keywords="web-scraping, materials, pricing, renovation, donizo",
    project_urls={
        "Bug Reports": "https://github.com/donizo/material-scraper/issues",
        "Source": "https://github.com/donizo/material-scraper",
        "Documentation": "https://github.com/donizo/material-scraper#readme",
    },
)
