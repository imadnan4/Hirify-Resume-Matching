import nltk
import logging
from typing import List


def download_nltk_data(force_download: bool = False) -> None:
    """Download required NLTK data."""
    logger = logging.getLogger(__name__)
    
    required_datasets = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'vader_lexicon'
    ]
    
    for dataset in required_datasets:
        try:
            nltk.data.find(f'tokenizers/{dataset}')
            if not force_download:
                logger.info(f"NLTK dataset '{dataset}' already exists")
                continue
        except LookupError:
            pass
        
        try:
            logger.info(f"Downloading NLTK dataset: {dataset}")
            nltk.download(dataset, quiet=True)
            logger.info(f"Successfully downloaded: {dataset}")
        except Exception as e:
            logger.error(f"Failed to download {dataset}: {str(e)}")


def check_nltk_data() -> List[str]:
    """Check which NLTK datasets are missing."""
    required_datasets = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'vader_lexicon'
    ]
    
    missing_datasets = []
    for dataset in required_datasets:
        try:
            nltk.data.find(f'tokenizers/{dataset}')
        except LookupError:
            missing_datasets.append(dataset)
    
    return missing_datasets


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Download NLTK data
    download_nltk_data()
    
    # Check for missing datasets
    missing = check_nltk_data()
    if missing:
        print(f"Missing NLTK datasets: {missing}")
    else:
        print("All NLTK datasets are available")
