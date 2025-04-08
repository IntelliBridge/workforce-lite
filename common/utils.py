import json
import logging
import os
import re
import time
from typing import Union, List
from datetime import datetime

import nltk
from nltk.stem import WordNetLemmatizer

nltk.download("punkt")
nltk.download("wordnet")

from common.vector_db import OpenSearchDB

logger = logging.getLogger(__name__)

def clean_and_transform_text(text: str) -> str:
    """
    Cleans and lemmatizes the text
    Param:
        text: string to be cleaned
    Returns:
        full_text: str fully cleaned text
    """
    # Remove unnecessary characters
    text.replace("\n", " ").replace("\x0b", "").replace("\xa0", "").strip()

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Tokenization
    words = re.findall(r"\s*(\w+|[^\w\s])\s*", text)

    # Instantiate word stemmer
    lemmatizer = WordNetLemmatizer()

    # Stems the words in the document
    words = [lemmatizer.lemmatize(word) for word in words]

    # Join the text back together
    joined_text = " ".join(words)

    # Correct unnecessary spaces in the newly joined text
    full_text = re.sub(r'\s+([,?.:;!%\'"])', r"\1", joined_text)
    full_text = re.sub(r"\(\s+", "(", full_text)
    full_text = re.sub(r"\s+\)", ")", full_text)
    full_text = re.sub(r"\s*-\s*", "-", full_text)
    full_text = full_text.replace(" '", "'")

    return full_text


def batch_bulk(index: int, chunks: list, vectorDB: OpenSearchDB) -> None:
    """
    Bulk ingests the data into OpenSearch by batch size
    Param:
        index: number that determines the size of the batches
        chunks: The chunks to be ingested
        vectorDB: vector database client that will perform
        the ingestion
        logger: used to log any errors, warnings, etc.
    """

    def bulk_insert(chunks, i, index=None, is_remainder=False):
        if is_remainder:
            try:
                # Bulk ingest the remainder of chunks
                vectorDB.client.bulk(chunks[i:], refresh=True)
            except Exception as e:
                logger.error(
                    f"An error occurred during bulk ingestion of the remainder of chunks: {e}"
                )
                logger.error(
                    f"It occurred at index {i}, and the range of chunks is from {i}:{len(chunks)}"
                )
                logger.error(f"Here are the chunks involved: {chunks[i:]}")

                secs = 5
                logger.info(f"Timeout for {secs} seconds. Will retry bulk ingestion")

                time.sleep(secs)

                logger.info(f"Retrying bulk ingestion")

                vectorDB.client.bulk(chunks[i:], refresh=True)
                    # Bulk ingest that range of chunks
                vectorDB.client.bulk(chunks[i - index : i], refresh=True)

                # Assign the remainder left to ingest
                remainder = i
            except Exception as e:
                logger.error(f"An error occurred during bulk ingestion: {e}")
                logger.error(
                    f"It occurred at index {i-index}, and the range of chunks is from {i-index}:{i}"
                )
                logger.error(f"Here are the chunks involved: {chunks[i-index:i]}")

                secs = 5
                logger.info(f"Timeout for {secs} seconds. Will retry bulk ingestion")

                time.sleep(secs)

                logger.info(f"Retrying bulk ingestion")

                vectorDB.client.bulk(chunks[i - index : i], refresh=True)

                # Assign the remainder left to ingest
                remainder = i
            return remainder
        else:
            try:
                # Bulk ingest that range of chunks
                vectorDB.client.bulk(chunks[i - index : i], refresh=True)

                # Assign the remainder left to ingest
                remainder = i
            except Exception as e:
                logger.error(f"An error occurred during bulk ingestion: {e}")
                logger.error(
                    f"It occurred at index {i-index}, and the range of chunks is from {i-index}:{i}"
                )
                logger.error(f"Here are the chunks involved: {chunks[i-index:i]}")

                secs = 5
                logger.info(f"Timeout for {secs} seconds. Will retry bulk ingestion")

                time.sleep(secs)

                logger.info(f"Retrying bulk ingestion")

                vectorDB.client.bulk(chunks[i - index : i], refresh=True)

                # Assign the remainder left to ingest
                remainder = i
            return remainder

    # If there is at least 1 chunk
    if len(chunks) > 0:
        for i in range(index, len(chunks), index):
            remainder = bulk_insert(chunks, i, index)

    else:
        logger.info("No chunks found to ingest")
        return

    bulk_insert(chunks, remainder, is_remainder=True)