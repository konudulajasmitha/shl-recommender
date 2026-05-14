# Updated for Render deployment
import numpy as np

class Retriever:
    def __init__(self):
        # Sample catalog - Replace this with your actual SHL test data
        self.catalog = [
            {"name": "Occupational Personality Questionnaire (OPQ)", "url": "https://www.shl.com/opq"},
            {"name": "Verify G+ Ability Test", "url": "https://www.shl.com/verify-g-plus"},
            {"name": "Senior Java Developer Assessment", "url": "https://www.shl.com/java-test"},
            {"name": "Management Situational Judgment Test", "url": "https://www.shl.com/sjt"}
        ]

    def search(self, query, top_k=3):
        """Simple keyword-based search to save memory."""
        query = query.lower()
        results = []
        
        for item in self.catalog:
            # Check if any words from the query match the test name
            if any(word in item['name'].lower() for word in query.split()):
                results.append(item)
        
        # If no keywords match, return the first few as defaults for the AI to pick from
        if not results:
            return self.catalog[:top_k]
            
        return results[:top_k]