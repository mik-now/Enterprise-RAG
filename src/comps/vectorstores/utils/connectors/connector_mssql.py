# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
import pyodbc
import json
from typing import Iterable, List, Optional, Union # noqa: F401
from comps.cores.proto.docarray import SearchedDoc, TextDoc # noqa: F401
from comps.cores.utils.utils import sanitize_env # noqa: F401
from comps.cores.utils.utils import get_boolean_env_var # noqa: F401
from comps.cores.mega.logger import get_opea_logger, change_opea_logger_level
from comps.vectorstores.utils.connectors.connector import VectorStoreConnector

logger = get_opea_logger(f"{__file__.split('comps/')[1].split('/', 1)[0]}")
change_opea_logger_level(logger, log_level=os.getenv("OPEA_LOGGER_LEVEL", "INFO"))

class ConnectorMssql(VectorStoreConnector):
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
        self.index_dict = {}
        self._client = None
        self.table_name = str(sanitize_env(os.getenv('MSSQL_VECTOR_TABLE', 'vdb')))
        self.dims = int(sanitize_env(str(os.getenv("VECTOR_DIMS", 768))))

        try:
            cursor = self.get_client().cursor()
            cursor.execute(self._vector_table_from_env())
            self.get_client().commit()
            cursor.close()
            logger.info(f"MSSQL table '{self.table_name}' is ready.")
        except Exception as e:
            logger.error(f"Error initializing MSSQL table: {e}")
            raise

    def get_client(self):
        if self._client is None:
            conn_string = os.getenv('MSSQL_URL')
            if not conn_string:
                raise ValueError("MSSQL_URL environment variable is not set.")

            try:
                self._client = pyodbc.connect(
                    'DRIVER={ODBC Driver 18 for SQL Server};'
                    f'{conn_string};'
                    'TrustServerCertificate=yes;'
                )
            except Exception as e:
                logger.error(f"Error connecting to MSSQL: {e}")
                raise
        return self._client

    def _vector_table_from_env(self) -> str:
        sql = f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.table_name}' AND xtype='U')
        CREATE TABLE {self.table_name} (
            id INT PRIMARY KEY IDENTITY(1,1),
            text NVARCHAR(MAX) not null,
            embedding VECTOR({self.dims}) not null,
            metadata NVARCHAR(MAX) null
        )
        """
        return sql

    async def add_texts(self, texts, embeddings, metadatas = None):
        try:
            cursor = self.get_client().cursor()
            table_name = self._vector_table_from_env()
            for text, embedding, metadata in zip(texts, embeddings, metadatas or [None]*len(texts)):
                cursor.execute(
                    f"""
                    INSERT INTO {self.table_name} (text, embedding, metadata)
                    VALUES (?, CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR({self.dims})), ?)
                    """,
                    text,
                    json.dumps(embedding), # needs to be string encoded json array
                    json.dumps(metadata) if metadata else "{}" # needs to be string encoded json object
                )
            self._client.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error connecting to MSSQL: {e}")
            raise

    async def search_and_delete_by_metadata(self, field_name: str, field_value: str):
        try:
            cursor = self.get_client().cursor()
            delete_query = f"DELETE FROM {self.table_name} WHERE JSON_VALUE(metadata, '$.{field_name}') = ?"
            cursor.execute(delete_query, field_value)
            self.get_client().commit()
            logger.info(f"Deleted {cursor.rowcount} record(s) from MSSQL where {field_name} = {field_value}")
            cursor.close()
        except Exception as e:
            logger.error(f"Error deleting from MSSQL: {e}")
            raise

    def _convert_to_text_doc(self, text, metadata, vector_distance) -> TextDoc:
        metadata = json.loads(metadata) if metadata else {}
        metadata["vector_distance"] = vector_distance
        return TextDoc(
            text=text,
            metadata=metadata
        )

    async def similarity_search_by_vector(self, input_text: str, embedding: List[float], k: int, distance_threshold: float = None, filter_expression =None, parse_result: bool = True) -> SearchedDoc:
        try:
            cursor = self.get_client().cursor()
            cursor.execute(
                f"""
                SELECT TOP ({k})
                    text,
                    metadata,
                    vector_distance('cosine', CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR({self.dims})), embedding) AS distance_score
                FROM {self.table_name}
                ORDER BY distance_score DESC
                """,
                json.dumps(embedding)
            )
            results = cursor.fetchall()
            cursor.close()

            retrieved_docs = []
            for row in results:
                text, metadata, distance_score = row
                retrieved_docs.append(self._convert_to_text_doc(text, metadata, distance_score))

            return SearchedDoc(
                retrieved_docs=retrieved_docs,
                user_prompt=input_text
            )
        except Exception as e:
            logger.error(f"Error searching in MSSQL: {e}")
            raise
