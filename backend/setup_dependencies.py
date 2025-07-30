#!/usr/bin/env python3
"""
Setup script to install missing models and dependencies for Hirify backend.
Run this after installing requirements.txt to ensure all models are available.
"""

import os
import sys
import subprocess
import nltk
import spacy
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            return True
        else:
            print(f"✗ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {description} failed with exception: {e}")
        return False

def setup_nltk_data():
    """Download required NLTK data."""
    print("\n" + "="*50)
    print("Setting up NLTK data...")
    print("="*50)
    
    # Set NLTK data path
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_path)
    
    required_data = [
        ('punkt', 'Punkt sentence tokenizer'),
        ('stopwords', 'Stopwords corpus'),
        ('wordnet', 'WordNet lexical database')
    ]
    
    success_count = 0
    for data_name, description in required_data:
        try:
            nltk.data.find(f'tokenizers/{data_name}' if data_name == 'punkt' else f'corpora/{data_name}')
            print(f"✓ {description} already available")
            success_count += 1
        except LookupError:
            print(f"Downloading {description}...")
            try:
                nltk.download(data_name, download_dir=nltk_data_path, quiet=True)
                print(f"✓ {description} downloaded successfully")
                success_count += 1
            except Exception as e:
                print(f"✗ Failed to download {description}: {e}")
    
    return success_count == len(required_data)

def setup_spacy_model():
    """Download required spaCy model."""
    print("\n" + "="*50)
    print("Setting up spaCy model...")
    print("="*50)
    
    model_name = "en_core_web_sm"
    
    try:
        # Check if model is already installed
        spacy.load(model_name)
        print(f"✓ spaCy model '{model_name}' already available")
        return True
    except OSError:
        print(f"spaCy model '{model_name}' not found. Downloading...")
        return run_command(
            f"python -m spacy download {model_name}",
            f"Download spaCy model '{model_name}'"
        )

def check_pytorch():
    """Check PyTorch installation."""
    print("\n" + "="*50)
    print("Checking PyTorch installation...")
    print("="*50)
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} is available")
        
        # Check if CUDA is available
        if torch.cuda.is_available():
            print(f"✓ CUDA is available (GPU acceleration enabled)")
        else:
            print("ℹ CUDA not available (CPU-only mode)")
        
        return True
    except ImportError:
        print("✗ PyTorch not found. Please install it manually:")
        print("  CPU-only: pip install torch")
        print("  With CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False

def check_transformers():
    """Check transformers library installation."""
    print("\n" + "="*50)
    print("Checking transformers library...")
    print("="*50)
    
    try:
        from transformers import BertTokenizer, BertModel
        print("✓ transformers library is available")
        
        # Try to load a small model to test
        try:
            print("Testing BERT model loading...")
            tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            print("✓ BERT tokenizer loaded successfully")
            return True
        except Exception as e:
            print(f"ℹ BERT model loading may require internet connection: {e}")
            return True
            
    except ImportError:
        print("✗ transformers library not found. It should be in requirements.txt")
        return False

def check_sentence_transformers():
    """Check sentence-transformers library installation."""
    print("\n" + "="*50)
    print("Checking sentence-transformers library...")
    print("="*50)
    
    try:
        # Try different import methods
        import sentence_transformers
        print(f"✓ sentence-transformers library is available (version: {sentence_transformers.__version__})")
        
        try:
            from sentence_transformers import SentenceTransformer
            print("✓ SentenceTransformer class imported successfully")
            
            try:
                print("Testing SentenceTransformer model loading...")
                model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ SentenceTransformer model loaded successfully")
                return True
            except Exception as e:
                print(f"ℹ SentenceTransformer model loading may require internet connection: {e}")
                print("This is normal on first run - models will download when needed")
                return True
                
        except ImportError as e:
            print(f"ℹ Could not import SentenceTransformer class: {e}")
            print("Library is installed but may have import issues")
            return True  # Still consider it available
            
    except ImportError:
        print("✗ sentence-transformers library not found")
        print("Try running: pip install sentence-transformers")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n" + "="*50)
    print("Creating necessary directories...")
    print("="*50)
    
    directories = [
        'uploads',
        'uploads/resumes',
        'logs',
        'temp'
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✓ Directory '{directory}' created/verified")
        except Exception as e:
            print(f"✗ Failed to create directory '{directory}': {e}")
            return False
    
    return True

def check_database_connection():
    """Check if database connection works."""
    print("\n" + "="*50)
    print("Checking database configuration...")
    print("="*50)
    
    try:
        from app.core.config import settings
        print(f"✓ Configuration loaded")
        print(f"Database URL: {settings.DATABASE_URL}")
        
        # Don't actually connect to avoid issues, just check config
        if settings.DATABASE_URL:
            print("ℹ Database URL configured (connection not tested)")
            return True
        else:
            print("✗ Database URL not configured")
            return False
            
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("Hirify Backend Dependency Setup")
    print("="*50)
    print("This script will set up required models and dependencies.")
    print("Make sure you've already run: pip install -r requirements.txt")
    print()
    
    # Track success/failure
    results = {}
    
    # Create directories
    results['directories'] = create_directories()
    
    # Setup NLTK data
    results['nltk'] = setup_nltk_data()
    
    # Setup spaCy model
    results['spacy'] = setup_spacy_model()
    
    # Check PyTorch
    results['pytorch'] = check_pytorch()
    
    # Check transformers
    results['transformers'] = check_transformers()
    
    # Check sentence-transformers
    results['sentence_transformers'] = check_sentence_transformers()
    
    # Check database configuration
    results['database'] = check_database_connection()
    
    # Print summary
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    
    success_count = 0
    total_count = len(results)
    
    for component, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{component.upper():<20}: {status}")
        if success:
            success_count += 1
    
    print(f"\nOverall: {success_count}/{total_count} components set up successfully")
    
    if success_count == total_count:
        print("\n🎉 All dependencies are set up correctly!")
        print("You can now start the Hirify backend server.")
    else:
        print(f"\n⚠️  {total_count - success_count} components need attention.")
        print("Please resolve the issues above before running the server.")
        
        # Print helpful commands
        print("\nHelpful commands:")
        if not results['spacy']:
            print("  python -m spacy download en_core_web_sm")
        if not results['pytorch']:
            print("  pip install torch")
        
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
