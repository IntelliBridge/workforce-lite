import logging
import os
import shutil
from datetime import datetime as dt

from common.file_reader import CustomDirectoryLoader
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()

NUM_DOWNLOAD = 5
FILE_FOLDER = config.FILE_FOLDER

def retrieve_extract_files():
    """
    Retrieves files from folder
    Extracts text from documents and unpacks the page content and metadata
    and writes to disk space.
    Returns:
        folder: Folder containing written documents
    """
    folder = f"retrieve_extract_files/job_{dt.now()}"
    os.makedirs(folder, exist_ok=True)
    
    # Instantiate FileLoader and declare where to write scraped text
    loader = CustomDirectoryLoader(FILE_FOLDER)

    # Scrape and write text
    loader.load(folder)

    logger.info(
        f"Number of Files Downloaded: {sum(len(files) for _, _, files in os.walk(FILE_FOLDER))}"
    )
    logger.info(
        f"Number of Files Scraped: {sum(len(files) for _, _, files in os.walk(folder))}"
    )
    
    return folder