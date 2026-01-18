#!/usr/bin/env python3
"""
Database management script for the Resume Parser application.
"""
import argparse
import logging
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database_utils import init_database, create_database, create_tables, seed_skills_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to handle command-line arguments and execute database operations."""
    parser = argparse.ArgumentParser(description='Database management for Resume Parser')
    parser.add_argument(
        'command',
        choices=['init', 'create-db', 'create-tables', 'seed-skills'],
        help='Database operation to perform'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            logger.info("Initializing database with all components...")
            init_database()
            logger.info("Database initialization completed successfully!")
            
        elif args.command == 'create-db':
            logger.info("Creating database...")
            create_database()
            logger.info("Database created successfully!")
            
        elif args.command == 'create-tables':
            logger.info("Creating tables...")
            create_tables()
            logger.info("Tables created successfully!")
            
        elif args.command == 'seed-skills':
            logger.info("Seeding skills data...")
            seed_skills_data()
            logger.info("Skills data seeded successfully!")
            
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
