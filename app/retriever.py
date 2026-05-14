import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self):
        path = 'app/catalog.json'
        if not os.path.exists(path):
            self.catalog = []
            self.index = None
            return
            
        with open(path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)
        
        if not self.catalog:
            self.index = None
            return

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.texts = [f"{c['name']} {c.get('description', '')}" for c in self.catalog]
        embeddings = self.model.encode(self.texts).astype('float32')
        
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, query, top_k=3):
        if not self.index:
            return []
        q_emb = self.model.encode([query]).astype('float32')
        D, I = self.index.search(q_emb, top_k)
        return [self.catalog[i] for i in I[0] if i != -1]