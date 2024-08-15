import numpy
from numpy.linalg import norm

class Memory:
    def __init__(self, vector_store):
        # {"id": 0, "data": [1278, 888,-111 ....]}
        self.embeddings = {}
        self.vector_store = vector_store

    def add_embedding(self, id, vectors):
        self.embeddings[id] = vectors

    def del_embedding(self, id):
        if id in self.embeddings:
            del self.embeddings[id]

    def search(self, text, count=5, filter={}):
        results = []
        question_vector = self.vector_store.embedder.embed(text)
        simularity = []
        a = numpy.array(question_vector)
        counter = 0
        for id in self.embeddings:
            b = numpy.array(self.embeddings[id])
            cosine = (numpy.dot(a,b)/(norm(a) * norm(b)))

            simularity.append({"id": id, "match": round(cosine * 100)})
            counter += 1

        sorted_data = sorted(simularity, key=lambda d: d['match'], reverse=True)

        return sorted_data[:count]

