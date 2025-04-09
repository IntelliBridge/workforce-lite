import logging
import os
import shutil

from common.disk_scripts import disk_loader, disk_writer
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def validate_clean_and_prep(clean_and_prep):
    """
    Validates that the data of the documents and metadata
    in each list is as expected to ensure downstream tasks function
    appropriately
    Param:
        clean_and_prep: Folder containing cleaned documents
    Returns:
        folder: Folder containing cleaned and validated documents
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
    folder = "validate_clean_and_prep"
    os.makedirs(folder, exist_ok=True)

    docs = []

    for blob in os.listdir(clean_and_prep):
        try:
            # Add documents to docs list from disk space
            disk_loader(docs, f"{clean_and_prep}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            # For each document and metadata in the list
            for i, (doc, meta) in enumerate(docs):
                assert_write(doc, meta, folder)
            docs = []

    # Validate and write to disk the remainder of files not processed in the for loop
    if docs:
        for i, (doc, meta) in enumerate(docs):
            assert_write(doc, meta, folder)

    # Delete previous folder
    shutil.rmtree(clean_and_prep)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )

    return folder
