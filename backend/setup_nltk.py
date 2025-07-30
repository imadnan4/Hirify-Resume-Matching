#!/usr/bin/env python3
"""
Script to ensure NLTK data is properly downloaded and available.
"""
import nltk
import os

def setup_nltk():
    """Download all required NLTK data."""
    
    # Set NLTK data path
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_path)
    
    # Download required packages
    packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    
    for package in packages:
        try:
            print(f"Downloading NLTK package: {package}")
            nltk.download(package, quiet=False)
            print(f"✓ Successfully downloaded {package}")
        except Exception as e:
            print(f"✗ Failed to download {package}: {e}")
    
    print("\nNLTK setup complete!")

if __name__ == "__main__":
    setup_nltk()
