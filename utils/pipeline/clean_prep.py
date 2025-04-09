import logging
import os
import shutil

from common.disk_scripts import disk_loader, disk_writer
from common.utils import clean_and_transform_text
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def clean_and_prep(validate_files):
    """
    Cleans the text removing unnecessary characters,
    stopwords, and lemmatizes the words.
    Param:
        validate_files: Folder containing validated documents
    Returns:
        folder: Folder containing cleaned documents
    """

    def clean_text_write(doc, folder, i):
        try:
            # Process text
            text = doc[0]

            full_text = clean_and_transform_text(text)

            doc[0] = full_text

            # Write documents to disk
            disk_writer(doc, folder)
        except Exception as e:
            logger.error(
                f"An error occurred with cleaning the text for file {doc[1]}: {e}"
            )
            logger.error(f"Encountered the file at index: {i}")

    # Folder to save files to
    folder = "clean_and_prep"
    os.makedirs(folder, exist_ok=True)

    docs = []

    for blob in os.listdir(validate_files):
        try:
            # Add documents to docs list from disk space
            disk_loader(docs, f"{validate_files}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            # For each doc in the files
            for i, doc in enumerate(docs):
                clean_text_write(doc, folder, i)
            docs = []

    # Clean and write to disk the remainder of files not processed in the for loop
    if docs:
        for i, doc in enumerate(docs):
            clean_text_write(doc, folder, i)

    # Delete previous folder
    shutil.rmtree(validate_files)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )

    return folder
