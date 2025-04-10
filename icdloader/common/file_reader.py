import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Type, Union

from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain_core.documents import Document

from common.disk_scripts import disk_writer
from configs.ollama_config import TaskConfig

logger = logging.getLogger(__name__)

config = TaskConfig()


class CustomDirectoryLoader(DirectoryLoader):
    """
    Enhanced DirectoryLoader that dynamically selects the appropriate loader class
    based on file extension.
    """

    def __init__(
        self,
        path: str,
        glob: Union[List[str], Sequence[str], str] = "**/[!.]*",
        silent_errors: bool = False,
        load_hidden: bool = False,
        recursive: bool = False,
        show_progress: bool = False,
        use_multithreading: bool = False,
        max_concurrency: int = 4,
        pdf_loader_cls: Type[BaseLoader] = PyPDFLoader,
        pdf_loader_kwargs: Dict[str, Any] = None,
        default_loader_cls: Type[BaseLoader] = UnstructuredFileLoader,
        default_loader_kwargs: Dict[str, Any] = None,
        file_extloader_mapping: Dict[str, Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize with path and configuration for different loaders.

        Args:
            path: Path to directory.
            glob: Glob pattern for file matching.
            silent_errors: Whether to silently ignore errors.
            load_hidden: Whether to load hidden files.
            recursive: Whether to search recursively.
            show_progress: Whether to show progress bar.
            use_multithreading: Whether to use multithreading.
            max_concurrency: Max number of threads.
            pdf_loader_cls: Loader class for PDF files.
            pdf_loader_kwargs: Kwargs for PDF loader.
            default_loader_cls: Default loader for non-PDF files.
            default_loader_kwargs: Kwargs for default loader.
            file_extloader_mapping: Optional mapping of file extensions to
                                    {loader_cls, loader_kwargs} dictionaries.
            **kwargs: Additional kwargs for DirectoryLoader.
        """
        # Initialize with dummy loader_cls that will be overridden in _lazy_load_file
        super().__init__(
            path=path,
            glob=glob,
            silent_errors=silent_errors,
            load_hidden=load_hidden,
            recursive=recursive,
            show_progress=show_progress,
            use_multithreading=use_multithreading,
            max_concurrency=max_concurrency,
            loader_cls=default_loader_cls,  # Will be dynamically replaced
            loader_kwargs={},  # Will be dynamically replaced
            **kwargs,
        )

        # Store loader configurations
        self.pdf_loader_cls = pdf_loader_cls
        self.pdf_loader_kwargs = pdf_loader_kwargs or {"mode": "single"}
        self.default_loader_cls = default_loader_cls
        self.default_loader_kwargs = default_loader_kwargs or {}

        # Optional mapping for additional file extensions
        self.file_extloader_mapping = file_extloader_mapping or {}

    def _write_data(self, doc, folder):
        try:
            # Format metadata
            # k = doc.metadata["source"]
            # d = doc.metadata["source"].split("/")
            meta = f"/{doc.metadata['source'].split('/')[-1]}"
            meta = {"source": meta}

            # Write file and metadata to folder
            disk_writer([doc.page_content, meta], folder)

        except Exception as e:
            logger.error(f"An error occurred in the load funtion: {e}")

    def load(self, folder) -> List[Document]:
        """
        Scrape text from documents.
        Augment document with associated metadata.
        Write scraped text and metadata to file in
        given folder.
        Param:
            folder: Target folder to write to
        """

        docs = []
        for document in self.lazy_load():
            if document:
                docs.extend([document])
            if len(docs) == config.MEM_BATCH_SIZE:
                for doc in docs:
                    self._write_data(doc, folder)
                docs = []
        if docs:
            for doc in docs:
                self._write_data(doc, folder)

    def _lazy_load_file(
        self, item: Path, path: Path, pbar: Optional[Any]
    ) -> Iterator[Document]:
        """
        Load a file with the appropriate loader based on its extension.

        Args:
            item: File path.
            path: Directory path.
            pbar: Progress bar.
        """
        if not item.is_file():
            return

        file_ext = item.suffix.lower()

        # Determine which loader and kwargs to use based on file extension
        if file_ext in self.file_extloader_mapping:
            # Use custom mapping if provided for this extension
            config = self.file_extloader_mapping[file_ext]
            loader_cls = config.get("loader_cls")
            loader_kwargs = config.get("loader_kwargs", {})
        elif file_ext == ".pdf":
            # Use PDF-specific loader
            loader_cls = self.pdf_loader_cls
            loader_kwargs = self.pdf_loader_kwargs
        else:
            # Use default loader
            loader_cls = self.default_loader_cls
            loader_kwargs = self.default_loader_kwargs

        try:
            logger.debug(f"Processing file {str(item)} with {loader_cls.__name__}")
            loader = loader_cls(str(item), **loader_kwargs)

            try:
                for subdoc in loader.lazy_load():
                    yield subdoc
            except NotImplementedError:
                for subdoc in loader.load():
                    yield subdoc

        except Exception as e:
            if self.silent_errors:
                logger.warning(f"Error loading file {str(item)}: {e}")
            else:
                logger.error(f"Error loading file {str(item)}")
                raise e
        finally:
            if pbar:
                pbar.update(1)
