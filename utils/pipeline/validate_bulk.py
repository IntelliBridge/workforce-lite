import logging
import os
import shutil

from common.disk_scripts import bulk_disk_loader, bulk_disk_writer
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def validate_bulk_preparation(bulk_preparation):
    """
    Validates the data is prepared to be bulk ingested
    by OpenSearch
    Param:
        bulk_preparation: Folder containing documents prepared for bulk ingestion into OpenSearch
    Returns:
        folder: Folder containing validated documents prepared for bulk ingestion into OpenSearch
    """

    def assert_write(docs, i):
        try:
            # Index into the current observation of the list.
            info = docs[i]

            # Starting and ending index of bulk prepped chunk
            leftCount = i
            rightCount = i + 2

            # Assert name of index is of type string
            assert type(info["index"]["_index"]) == str

            # Upload bulk chunks to disk space
            bulk_disk_writer(docs[leftCount:rightCount], folder)

        except AssertionError as e:
            logger.error(
                f"An assertion error occurred while validating that the data was prepared for bulk ingestion: {e}"
            )

    # Folder to save files to
    folder = "validate_bulk_preparation"
    os.makedirs(folder, exist_ok=True)

    docs = []

    for blob in os.listdir(bulk_preparation):
        try:
            # Add bulk chunks to docs list from disk space
            bulk_disk_loader(docs, f"{bulk_preparation}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the bulk_disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            try:
                # Test if an even amount of elements are in the list.
                assert len(docs) % 2 == 0
            except AssertionError as e:
                logger.error(
                    f"After bulk_preparation there should and must be an even amount of elements in the list: {e}"
                )
                logger.error(f"Number of elements in list: {len(docs)}")
                raise AssertionError(f"Error: {e}")

            # Loop through the list by 2
            for i in range(0, len(docs), 2):
                assert_write(docs, i)
            docs = []

    # Validate and write to disk the remainder of files not processed in the for loop
    if docs:
        try:
            # Test if an even amount of elements are in the list.
            assert len(docs) % 2 == 0
        except AssertionError as e:
            logger.error(
                f"After bulk_preparation there should and must be an even amount of elements in the list: {e}"
            )
            logger.error(f"Number of elements in list: {len(docs)}")
            raise AssertionError(f"Error: {e}")

        # Loop through the list by 2
        for i in range(0, len(docs), 2):
            assert_write(docs, i)
    # Delete previous folder
    shutil.rmtree(bulk_preparation)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )

    return folder
