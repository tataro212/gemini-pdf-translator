#!/usr/bin/env python3
"""
Simple tool to clear translation caches
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    cache_files = ['translation_cache.json']
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info(f"✅ Cleared: {cache_file}")
            except Exception as e:
                logger.error(f"❌ Failed: {cache_file} - {e}")
        else:
            logger.info(f"ℹ️ Not found: {cache_file}")
    
    logger.info("🚀 Ready for fresh processing!")

if __name__ == "__main__":
    main()
