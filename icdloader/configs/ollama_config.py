import os
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv


class EnvVarNotFoundError(Exception):
    """Raised when a required environment variable is not found."""

    pass


@dataclass
class TaskConfig:
    """Configuration for data pipeline task parameters loaded from environment variables."""

    def __init__(self):
        """
        Initialize configuration from environment variables.
        """
        # Load environment variables from file
        load_dotenv(find_dotenv())

        # Settings
        self.MEM_BATCH_SIZE = int(os.getenv("MEM_BATCH_SIZE", 50))
        self.INGEST_MAX_BATCH_SIZE = int(os.getenv("INGEST_MAX_BATCH_SIZE", 100))

        # OpenSearch Variables
        self.OS_URL = self._get_required_env("OS_URL")
        self.OS_USERNAME = self._get_required_env("OS_USERNAME")
        self.OS_PASSWORD = self._get_required_env("OS_PASSWORD")
        self.INDEX_NAME = self._get_required_env("INDEX_NAME")

        # File Store
        self.FILE_FOLDER = self._get_required_env("FILE_FOLDER")

        # Embedding Variables
        self.MODEL_NAME = self._get_required_env("MODEL_NAME")

    @staticmethod
    def _get_required_env(var_name: str) -> str:
        """Get a required environment variable or raise an error."""
        value = os.getenv(var_name)
        if value is None:
            raise EnvVarNotFoundError(
                f"Required environment variable '{var_name}' not found"
            )
        return value
