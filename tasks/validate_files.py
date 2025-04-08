import logging
import os
import shutil
from datetime import datetime as dt

from common.disk_scripts import disk_loader, disk_writer
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def validate_files(retrieve_extract_files):
    """
    Validates that the data of the documents and metadata
    is as expected to ensure downstream tasks function
    appropriately
    Param:
        retrieve_extract_files: Folder containing written documents
    Returns:
        folder: Folder containing validated documents
    """

    def assert_write(doc, meta, folder):
        try:
            # Assert document is of type string
            assert type(doc) == str
            # Assert the length of the document is at least 1
            assert len(doc) > 0
            # Assert the metadata is the correct type of dict
            assert type(meta) == dict
            # Assert that the source of the document is of type string
            assert type(meta["source"]) == str
            # Write documents to disk
            disk_writer([doc, meta], folder)

        except AssertionError as e:
            logger.error(
                f"An assertion error occurred while validating the documents from disk space: {e}"
            )
            logger.error(f"The file that rose the error was: {meta}")
            logger.error(
                f"Encountered the file at index {i} and it will not be written to disk"
            )

    # Folder to save files to
    folder = f"validate_files/job_{dt.now()}"
    os.makedirs(folder, exist_ok=True)

    docs = []

    for blob in os.listdir(retrieve_extract_files):
        try:
            # Add documents to docs list from disk space
            disk_loader(docs, f"{retrieve_extract_files}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            for i, (doc, meta) in enumerate(docs):
                assert_write(doc, meta, folder)
            docs = []

    # Validate and write to disk the remainder of files not processed in the for loop
    if docs:
        for i, (doc, meta) in enumerate(docs):
            assert_write(doc, meta, folder)

    # Delete previous folder
    shutil.rmtree(retrieve_extract_files)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )
    return folder