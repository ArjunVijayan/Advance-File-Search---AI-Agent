import os

import csv
import chromadb

import pandas as pd
import numpy as np

from chromadb.utils import embedding_functions
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


class VectorDB:
    
    def __init__(self, data):
        self.data = data
        self.collection = None

    def generate_data(self):

        lines = csv.reader(self.data)
    
        documents = []
        metadatas = []
        ids = []
        
        id = 1
    
        for i, row in self.data.iterrows():
            line = row.values
            metadatas.append(
                {
                    "author": line[0], 
                    "source": line[1],
                    "file_title": line[2], 
                    "file_size": line[3], 
                    "file_type": line[4], 
                    "file_location_at_source": line[5], 
                    "file_created_at": line[6], 
                    "file_last_updated_at": line[7], 
                    "file_url": line[8]
                })
            
            ids.append(str(id))
            id+=1
    
        documents = self.data["generated_insights"].values.tolist()
                
        return ids, documents, metadatas
        
    def create_db(self):
        
        ids, documents, metadatas = self.generate_data()
        chroma_client = chromadb.PersistentClient(path="my_vectordb")
        
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
        collection = chroma_client.get_or_create_collection(name="my_collection3", embedding_function=sentence_transformer_ef)
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        self.collection = collection

    def send_query(self, query_text, constraint=None):

        query_texts = [query_text]

        if 'and' in query_text.lower():
            query_texts = query_text.lower().split("and")

        if 'or' in query_text.lower():
            query_texts = query_text.lower().split("or")

        if constraint != None:

            query_response = self.collection.query(query_texts=query_texts, 
            n_results=10, include=['documents', 'embeddings', 'metadatas'])

        else:

            query_response = self.collection.query(query_texts=query_texts,
            n_results=10,
            where=constraint
            , include=['documents', 'embeddings', 'metadatas'])
            
        return query_response

    def send_query_with_constraint(self, query_text, contraint, n_results=1):
        results = self.collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"metadata_field": "is_equal_to_this"})

        return results

    def get_all(self, contraint):

        results = self.collection.get(
            include=["metadatas"],
            where=contraint)

        return results