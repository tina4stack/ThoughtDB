import numpy
import json
from numpy.linalg import norm


class Memory:
    def __init__(self, vector_store):
        # {"id": 0, "data": [1278, 888,-111 ....]}
        self.embeddings = {}
        self.vector_store = vector_store

    def add_embedding(self, id, vectors):
        if isinstance(vectors, str):
            vectors = json.loads(vectors)
        self.embeddings[id] = vectors

    def del_embedding(self, id):
        if id in self.embeddings:
            del self.embeddings[id]

    @staticmethod
    def get_distance(vector_a, vector_b):
        a = numpy.array(vector_a)
        b = numpy.array(vector_b)
        cosine = (numpy.dot(a, b) / (norm(a) * norm(b)))
        return round(cosine * 100)

    def search(self, text, count=5, filter=[]):
        results = []
        question_vector = self.vector_store.embedder.embed(text)
        similarity = []
        counter = 0
        for id in self.embeddings:

            if len(filter) > 0:
                if id in filter:
                    score = Memory.get_distance(question_vector, self.embeddings[id])
                    similarity.append({"id": id, "match": score})
                    counter += 1
            else:
                score = Memory.get_distance(question_vector, self.embeddings[id])
                similarity.append({"id": id, "match": score})
                counter += 1

        sorted_data = sorted(similarity, key=lambda d: d['match'], reverse=True)

        return sorted_data[:count]
