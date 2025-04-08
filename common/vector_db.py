import json
import os
import re
from typing import List, Union

import requests
from dotenv import find_dotenv, load_dotenv
from langchain_core.documents import Document
from opensearchpy import Index, OpenSearch

class OpenSearchDB:
    """Customized OpenSearch class"""

    def __init__(
        self, os_url: str, username: str, password: str, index_name: str, swap=False
    ) -> None:
        """
        Initialize OpenSearch index with configuration parameters and assign index_name attribute.

        Param:
            host: str
                Where OpenSearch is hosted
            port: str
                What port to reach
            index_name: str
                name of index

        Attrib:
            newindex: bool
                Determine if OpenSearch index already existed
        """
        self.client: OpenSearch = self._get_client(os_url, username, password)
        self.index_name = index_name
        self.index, self.newIndex = self._get_or_create_index(index_name, swap=swap)

    def _get_client(self, os_url: str, username: str, password: str):
        try:
            # Connect to OpenSearch DB
            client = OpenSearch(
                hosts=[os_url],
                http_auth=(username, password),
                verify_certs=True,
                timeout=60,
                max_retries=10,
                retry_on_timeout=True,
            )
            client.ping()
        except:
            raise Exception(
                "Cannot connect to the Vector Database. Is the service stood up?"
            )
        return client

    def _get_or_create_index(self, index_name: str, swap=False) -> Union[Index, bool]:
        """
        Get or create OpenSearch index

        Param:
            host: Where OpenSearch is hosted
            port: What port to reach

        Returns:
            tuple: (index, bool)

        Attrib:
            index_name: Name of index
        """
        # Get index name
        index_name = self.index_name

        # If we're changing indexes.
        if swap:
            # If index is found
            if self.client.indices.exists(index_name):
                # Return existing index
                index = Index(index_name)
                return index, False
            else:
                # index does not exist in vector database
                raise (ValueError(f"A index named: {index_name}, was not found."))
        else:
            # If index is found
            if self.client.indices.exists(index_name):
                # Return existing index
                index = Index(index_name)
                return index, False

        # Create fields for index
        index_body = {
            "settings": {"index": {"knn": True, "knn.algo_param.ef_search": 512}},
            "mappings": {  # how do we store,
                "properties": {
                    "text":{
                        "type": "text"
                    },
                    "vector_field": {
                        "type": "knn_vector",  # we are going to put
                        "dimension": 1536,
                        "method": {
                            "name": "hnsw",
                            "space_type": "l2",
                            "engine": "nmslib",
                            "parameters": {"ef_construction": 512, "m": 16},
                        },
                    }
                }
            },
        }
        self.client.indices.create(index=index_name, body=index_body)

        return Index(index_name), True

    def load_context(self, embeddings_list: List[float], query_text: str, index_name: str) -> str:
        """
        Perform similarity search, obtain context,
        and return it

        Param:
            embeddings_list: List of embedding values

        Returns:
            context: Related subject matter to embedding values
        """
        # Searching parameters
        query_body = {
            "size": 10,
            "query": {
                "hybrid": {
                    "queries": [
                    {
                        "match": {
                            "text": query_text
                        }
                    },
                    {
                        "knn": {
                            "vector_field": {
                                "vector": embeddings_list[0],
                                "k": 10
                            }
                        }
                    }
                    ]
                },
            },
            "_source": False,
            "fields": ["text", "metadata"],
        }
        

        # Similarity search
        context = self.client.search(body=query_body, index=index_name)

        res = []
        # # Join the list comprehensions into one string
        for key in context["hits"]["hits"]:
            text = key["fields"]["text"][0]
            # Process text
            text.replace("\n", " ").replace("\r", " ").replace("\f", "").strip()

            # Remove multiple spaces
            text = re.sub(r"\s+", " ", text)
            meta = json.loads(key["fields"]["metadata"][0])

            new_dict = {**{"Text": text}, **meta}

            res.append(new_dict)

        return json.dumps(res)

    def connected(self) -> bool:
        """
        Perform health check to see if connection
        to OpenSearch exists

        Returns:
            isConnected: Boolean determining if connection
            exists.
        """
        return self.client.ping()

    def drop(self, index_name: str) -> None:
        """
        Drops designated index from vector database

        Param:
            index_name: name of index
        """
        # Check if index is present in database
        if self.client.indices.exists(index_name):
            # Drop the index
            self.client.indices.delete(index_name)
        else:
            # Raise error that index was not found
            raise (ValueError(f"An index named: {index_name}, was not found."))

    def list_indices(self) -> List[str]:
        return list(self.client.indices.get_alias("*"))
