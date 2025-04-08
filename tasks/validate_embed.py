import logging
import os
import shutil
from datetime import datetime as dt

from common.disk_scripts import chunk_disk_loader, chunk_disk_writer
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def validate_embed_files(embed_files):
    """
    Validates the data types in the data
    and ensures uniqueness using continually incrementing
    id
    Param:
        embed_files: Folder containing chunked documents
    Returns:
        folder: Folder containing validated and chunked documents
    """

    def assert_write(obs, folder, blob_index):
        try:
            # Assert text is of type string
            assert type(obs["text"]) == str
            # Assert embedding list is of type list and the values are floats
            assert isinstance(obs["vector_field"], list) and all(
                isinstance(x, float) for x in obs["vector_field"]
            )
            # Assert the metadata is of type str
            assert type(obs["metadata"]) == str

            # Write chunks to disk space
            chunk_disk_writer(
                [obs["text"], obs["vector_field"], obs["metadata"]],
                folder,
                blob_index,
            )

        except AssertionError as e:
            logger.error(
                f"An assertion error occurred while validating the embedded chunks: {e}"
            )
            logger.error(f"The chunk that rose the error was: {obs}")
            logger.error(
                f"Encountered the file at index {i} and it will not be written to disk"
            )

    # Folder to save files to
    folder = f"validate_embed_files/job_{dt.now()}"
    os.makedirs(folder, exist_ok=True)

    docs = []

    blob_index = -1

    for blob in os.listdir(embed_files):
        try:
            # Add chunks to docs list from disk space
            chunk_disk_loader(docs, f"{embed_files}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the chunk_disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            for i, obs in enumerate(docs):
                blob_index += 1
                assert_write(obs, folder, blob_index)
            docs = []

    # Validate and write to disk the remainder of files not processed in the for loop
    if docs:
        for i, obs in enumerate(docs):
            blob_index += 1
            assert_write(obs, folder, blob_index)

    # Delete previous folder
    shutil.rmtree(embed_files)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )
    return folder