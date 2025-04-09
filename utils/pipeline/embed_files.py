import json
import logging
import os
import shutil

from langchain_ollama import OllamaEmbeddings

from common.disk_scripts import chunk_disk_writer, disk_loader
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()

# Chunking Variables
CHUNK_SIZE = 1024
OVERLAP = 512


def embed_files(validate_clean_and_prep):
    """
    Chunks the documents, embeds the chunks,
    Formats the data properly
    Param:
        validate_clean_and_prep: Folder containing cleaned and validated documents
    Returns:
        folder: Folder containing chunked documents
    """

    def embed_write(doc, embedder):
        text, metadata = doc

        metadata = json.dumps(metadata)

        # Create chunks
        chunks = [
            text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE - OVERLAP)
        ]

        try:
            # Post request to embedding service with all chunks
            embeddings_list = embedder.embed_documents(chunks)

        except Exception as e:
            logger.error(
                f"An error occurred in the request to the embedding service: {e}"
            )
            return

        for i, chunk in enumerate(chunks):
            try:
                # Write chunks to disk space
                chunk_disk_writer([chunk, embeddings_list[i], metadata], folder, i)

            except Exception as e:
                logger.error(
                    f"There was an error in the chunk_disk_writer function: {e}"
                )

    # Folder to save files to
    folder = "embed_files"
    os.makedirs(folder, exist_ok=True)

    docs = []

    embedder = OllamaEmbeddings(model=config.MODEL_NAME)

    for blob in os.listdir(validate_clean_and_prep):
        try:
            # Add documents to docs list from disk space
            disk_loader(docs, f"{validate_clean_and_prep}/{blob}")
        except Exception as e:
            logger.error(f"There was an error in the disk_loader function: {e}")
            continue

        if len(docs) == config.MEM_BATCH_SIZE:
            for doc in docs:
                embed_write(doc, embedder)
            docs = []

    # Embed and write to disk the remainder of files not processed in the for loop
    if docs:
        for doc in docs:
            embed_write(doc, embedder)

    # Delete previous folder
    shutil.rmtree(validate_clean_and_prep)

    logger.info(
        f"Number of Files Processed: {sum(len(files) for _, _, files in os.walk(folder))}"
    )

    return folder
