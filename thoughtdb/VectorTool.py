#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#

from llama_cpp import Llama
import numpy
from numpy.linalg import norm

global vector_llm

vector_llm = None


class VectorTool:

    @staticmethod
    def load_model(model_path="./nomic-embed-text-v1.5.Q4_K_M.gguf"):
        global vector_llm
        if vector_llm is None:
            vector_llm = Llama(
                model_path,
                n_gpu_layers=33,
                n_ctx=1024,
                n_batch=1024,
                n_threads=64,
                verbose=False,
                embedding=True
            )

        return vector_llm

    @staticmethod
    def get_vector(text):
        global vector_llm
        embedding = vector_llm.create_embedding(text)
        if len(embedding["data"][0]["embedding"]) > 0:
            return embedding["data"][0]["embedding"]
        else:
            return []

    @staticmethod
    def get_vectors(sentences):
        vectors = []
        for sentence in sentences:
            vectors.append(VectorTool.get_vector(sentence.strip()))
        return vectors

    @staticmethod
    def get_vector_match(question, vectors, count=5):
        global vector_llm
        if isinstance(question, str):
            question_vector = VectorTool.get_vector(question)
        else:
            question_vector = question

        similarity = []
        input_text = numpy.array(question_vector)
        counter = 0
        for vector in vectors:
            if isinstance(vector, str):
                vector = VectorTool.get_vector(vector)

            vector_text = numpy.array(vector)
            cosine = (numpy.dot(input_text, vector_text) / (norm(input_text) * norm(vector_text)))

            similarity.append({"index": counter, "match": round(cosine * 100)})
            counter += 1

        sorted_data = sorted(similarity, key=lambda d: d['match'], reverse=True)

        return sorted_data[:count]
