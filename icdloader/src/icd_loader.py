from configs.ollama_config import TaskConfig
from utils.pipeline.bulk_prep import bulk_preparation
from utils.pipeline.clean_prep import clean_and_prep
from utils.pipeline.embed_files import embed_files
from utils.pipeline.ingest import ingest_data
from utils.pipeline.retrieve_extract import retrieve_extract_files
from utils.pipeline.validate_bulk import validate_bulk_preparation
from utils.pipeline.validate_clean import validate_clean_and_prep
from utils.pipeline.validate_embed import validate_embed_files
from utils.pipeline.validate_files import validate_files
from utils.pipeline.validate_ingest import validate_ingest_data

config = TaskConfig()


class ICDLoader:
    def __init__(self, file_store: str = config.FILE_FOLDER):
        self.file_store = file_store

    def sync(self):
        folder = retrieve_extract_files(self.file_store)
        folder = validate_files(folder)
        folder = clean_and_prep(folder)
        folder = validate_clean_and_prep(folder)
        folder = embed_files(folder)
        folder = validate_embed_files(folder)
        folder = bulk_preparation(folder)
        folder = validate_bulk_preparation(folder)
        payload = ingest_data(folder)
        validate_ingest_data(payload["doc_count"], payload["pre_existing_chunks"])
