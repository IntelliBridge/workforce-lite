import logging
import os
import shutil

from common.file_reader import CustomDirectoryLoader
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()

NUM_DOWNLOAD = 5


def retrieve_extract_files(file_store):
    """
    Retrieves files from folder
    Extracts text from documents and unpacks the page content and metadata
    and writes to disk space.
    Param:
        file_store: Folder containing original documents
    Returns:
        folder: Folder containing written documents
    """
    folder = "retrieve_extract_files"
    os.makedirs(folder, exist_ok=True)

    # Instantiate FileLoader and declare where to write scraped text
    loader = CustomDirectoryLoader(file_store)

    # Scrape and write text
    loader.load(folder)

    logger.info(
        f"Number of Files Stored: {sum(len(files) for _, _, files in os.walk(file_store))}"
    )
    logger.info(
        f"Number of Files Scraped: {sum(len(files) for _, _, files in os.walk(folder))}"
    )

    return folder
