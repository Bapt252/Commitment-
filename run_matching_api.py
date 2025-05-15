#!/usr/bin/env python
"""
Run script for the SmartMatch API.

This script sets up and runs the FastAPI application for SmartMatch.
"""

import os
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run the SmartMatch API."""
    # Get configuration from environment variables
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5052"))
    reload = os.environ.get("RELOAD", "False").lower() in ("true", "1", "t")
    
    logger.info(f"Starting SmartMatch API on {host}:{port} (reload={reload})")
    
    # Start the server
    uvicorn.run(
        "app.adapters.matching_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
