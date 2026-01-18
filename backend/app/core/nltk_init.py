"""
NLTK initialization module to ensure required data is available.
"""
import os
import nltk
from typing import List

def ensure_nltk_data() -> bool:
    """
    Ensure all required NLTK data is downloaded and available.
    Uses caching - only downloads if data is missing.
    
    Returns:
        bool: True if all data is available, False otherwise
    """
    # Set NLTK data path
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_path)
    
    # Also add current directory path for NLTK data
    current_dir_nltk = os.path.join(os.getcwd(), 'nltk_data')
    if current_dir_nltk not in nltk.data.path:
        nltk.data.path.insert(0, current_dir_nltk)
    
    # Required packages
    required_packages = [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet'),
        ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger')
    ]
    
    all_available = True
    missing_packages = []
    
    for data_path, package_name in required_packages:
        try:
            # Try to find the data - silent check
            nltk.data.find(data_path)
        except LookupError:
            missing_packages.append(package_name)
    
    # Only download missing packages
    if missing_packages:
        print(f"Downloading missing NLTK packages: {', '.join(missing_packages)}")
        for package_name in missing_packages:
            try:
                nltk.download(package_name, quiet=True)
            except Exception as e:
                print(f"Failed to download NLTK package {package_name}: {e}")
                all_available = False
    
    return all_available

# Initialize NLTK data when this module is imported
_NLTK_INITIALIZED = False

def init_nltk():
    """Initialize NLTK data once."""
    global _NLTK_INITIALIZED
    if not _NLTK_INITIALIZED:
        ensure_nltk_data()
        _NLTK_INITIALIZED = True

# Auto-initialize when imported
init_nltk()
