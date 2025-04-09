import logging

from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()

FILE_FOLDER = config.FILE_FOLDER


def validate_ingest_data(doc_count, pre_existing_chunks):
    """
    Validates the number of chunks ingested match
    the number of chunks expected to be ingested.
    Param:
        doc_count: Number of chunks ingested into OpenSearch
        pre_existing_chunks: Number of chunks that already existed in the OpenSearch index
    """
    from common.vector_db import OpenSearchDB

    vectorDB = OpenSearchDB(
        os_url=config.OS_URL,
        username=config.OS_USERNAME,
        password=config.OS_PASSWORD,
        index_name=config.INDEX_NAME,
    )

    logger.info(f"Number of chunks prior to ingestion: {pre_existing_chunks}")

    try:
        logger.info(
            f'Number of chunks after ingestion into OpenSearch: {vectorDB.client.count(index=config.INDEX_NAME)["count"]}'
        )
    except Exception as e:
        logger.error(
            f"An error occurred trying to get the count of chunks ingested into the vector database: {e}"
        )

    logger.info(
        f"Number of chunks expected to have been ingested this run: {doc_count}"
    )

    try:
        assert vectorDB.client.count(index=config.INDEX_NAME)["count"] == doc_count
    except AssertionError as e:
        logger.error(
            f"An assertion error occurred when testing if the number of chunks ingested matches the number of chunks expected to be ingested: {e}"
        )
