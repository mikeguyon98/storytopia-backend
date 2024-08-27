from sqlalchemy import URL
from llama_index.vector_stores.tidbvector import TiDBVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Document
from typing import Optional, List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pymysql

class TiDBVectorService:
    def __init__(self, username, password, host, database="test"):
        self.connection_url = URL(
            "mysql+pymysql",
            username=username,
            password=password,
            host=host,
            port=4000,
            database=database,
            query={"ssl_verify_cert": True, "ssl_verify_identity": True},
        )
        self.vector_store = None
        self.vector_index = None
        self.storage_context = None
        self.query_engine = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(pymysql.err.OperationalError)
    )
    def get_vector_store(self, user_id: str):
        self.vector_store = TiDBVectorStore(
            connection_string=self.connection_url,
            table_name=user_id,
            distance_strategy="cosine",
            vector_dimension=1536,
            drop_existing_table=False,
        )
        return self.vector_store

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(pymysql.err.OperationalError)
    )
    def setup_index(self, user_id: Optional[str] = None):
        if not self.vector_store and user_id:
            self.get_vector_store(user_id)
        elif not self.vector_store and not user_id:
            raise ValueError(
                "Vector store not set up. Please provide a user_id or call get_vector_store() first."
            )

        self.vector_index = VectorStoreIndex.from_vector_store(self.vector_store)
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        self.query_engine = self.vector_index.as_query_engine(streaming=True)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(pymysql.err.OperationalError)
    )
    def add_documents(
        self,
        documents: List[Document],
        metadata: Optional[Dict[str, Any]] = None,
        show_progress: bool = True,
    ):
        if not self.vector_index or not self.storage_context:
            raise ValueError(
                "Index and storage context not set up. Call setup_index() first."
            )

        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)

        self.vector_index = self.vector_index.from_documents(
            documents, storage_context=self.storage_context, show_progress=show_progress
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(pymysql.err.OperationalError)
    )
    def query(self, query_string: str):
        if not self.query_engine:
            raise ValueError("Query engine not set up. Call setup_index() first.")

        return self.query_engine.query(query_string)