import logging
import os
import shutil
import time

from common.disk_scripts import bulk_disk_loader
from common.utils import batch_bulk
from common.vector_db import OpenSearchDB
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


def ingest_data(validate_bulk_preparation):
    """
    Bulk ingests the data into OpenSearch
    Param:
        validate_bulk_preparation: Folder containing validated documents
        prepared for bulk ingestion into OpenSearch
    Returns:
        doc_count: Number of chunks ingested into OpenSearch
        pre_existing_chunks: Number of chunks that already existed in the OpenSearch index
    """

    def track_values(docs, doc_count, batch_count):
        doc_length = len(docs) // 2
        doc_count += doc_length
        batch_count += 1

        return doc_length, doc_count, batch_count

    def calc_index(doc_length, max_batch):
        index = doc_length - 1 if doc_length < max_batch else max_batch
        index = index if index % 2 == 0 else index - 1
        index = 2 if index <= 1 else index

        return index

    def perform_ingestion(docs, doc_count, batch_count):
        doc_length, doc_count, batch_count = track_values(docs, doc_count, batch_count)

        # Set index to 1 minus doc_length if doc_length < config.INGEST_MAX_BATCH_SIZE or
        # set it to config.INGEST_MAX_BATCH_SIZE if doc_length >= config.INGEST_MAX_BATCH_SIZE
        index = calc_index(doc_length, config.INGEST_MAX_BATCH_SIZE)
        logger.info(f"Current Batch Size For Batch {batch_count}: {index}")

        start = time.perf_counter()
        # Bulk ingestion into OpenSearch
        batch_bulk(index, docs, vectorDB)
        end = time.perf_counter()

        logger.info(
            f"Amount of time taken to index into OpenSearch for batch {batch_count}: {end - start}"
        )

        logger.info(
            f"Number of failed inserts for batch {batch_count}: {(pre_existing_chunks + doc_count) - vectorDB.client.count(index=config.INDEX_NAME)['count']}"
        )

        print()

        return doc_count, batch_count

    vectorDB = OpenSearchDB(
        os_url=config.OS_URL,
        username=config.OS_USERNAME,
        password=config.OS_PASSWORD,
        index_name=config.INDEX_NAME,
    )

    docs = []

    pre_existing_chunks = vectorDB.client.count(index=config.INDEX_NAME)["count"]
    doc_count = 0
    batch_count = 0

    for blob in os.listdir(validate_bulk_preparation):
        try:
            # Add bulk chunks to docs list
            bulk_disk_loader(docs, f"{validate_bulk_preparation}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the bulk_disk_loader function: {e}")
            continue

        if len(docs) == config.INGEST_MAX_BATCH_SIZE:
            doc_count, batch_count = perform_ingestion(docs, doc_count, batch_count)
            docs = []

    # Ingest the remainder of files not processed in the for loop
    if docs:
        doc_count, batch_count = perform_ingestion(docs, doc_count, batch_count)

    # Delete previous folder
    shutil.rmtree(validate_bulk_preparation)

    return {"doc_count": doc_count, "pre_existing_chunks": pre_existing_chunks}
