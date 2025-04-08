import logging
import os
import shutil
from datetime import datetime as dt

from common.disk_scripts import bulk_disk_writer, chunk_disk_loader
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def bulk_preparation(validate_embed_files):
    """
    Prepares the data for bulk ingestion, by adding
    instructions OpenSearch requires for the operation.
    Ensures uniqueness in OpenSearch by using continually incrementing id
    Param:
        validate_embed_files: Folder containing validated and chunked documents
    Returns:
        folder: Folder containing documents prepared for bulk ingestion into OpenSearch
    """

    def perform_prep(doc):
        try:
            bulk_array = []

            # Append dictionary instructions to the list and the actual chunks.
            bulk_array.append({"index": {"_index": config.INDEX_NAME}})
            bulk_array.append(doc)

            # Upload bulk chunks to disk space
            bulk_disk_writer(bulk_array, folder)

        except Exception as e:
            logger.error(
                f"An error occurred while preparing the data for bulk ingestion: {e}"
            )
            logger.error(f"The chunk that rose the error was: {doc}")

    # Folder to save files to
    folder = f"bulk_preparation/job_{dt.now()}"
    os.makedirs(folder, exist_ok=True)

    docs = []

    for blob in os.listdir(validate_embed_files):
        try:
            # Add chunks to docs list from disk space
            chunk_disk_loader(docs, f"{validate_embed_files}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the chunk_disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            for i in range(len(docs)):
                perform_prep(docs[i])
            docs = []

    # Prep docs for bulk ingestion and write to disk the remainder of files not processed in the for loop
    if docs:
        for i in range(len(docs)):
            perform_prep(docs[i])

    # Delete previous folder
    shutil.rmtree(validate_embed_files)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )
    return folder