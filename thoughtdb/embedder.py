import numpy as np
from thought.model_loader import load_model


class Embedder:
    """Wraps the embedding model. Handles single + batch embedding with query caching."""

    def __init__(self, model_path="./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf"):
        self.model = load_model(model_path, verbose=False, embedding=True)
        self.model_name = model_path.split("/")[-1]
        self._last_text = None
        self._last_vector = None

    def embed(self, text):
        """Embed a single text string. Returns list of floats. Caches last query."""
        if text == self._last_text and self._last_vector is not None:
            return self._last_vector
        vector = self.model.embed(text)
        self._last_text = text
        self._last_vector = vector
        return vector

    def embed_batch(self, texts):
        """Embed multiple texts. Returns list of float lists."""
        return [self.embed(t) for t in texts]

    @property
    def dimensions(self):
        """Return the embedding dimension count."""
        test = self.embed("test")
        return len(test)

    @staticmethod
    def to_bytes(vector):
        """Convert float list to binary blob for sqlite-vec."""
        return np.array(vector, dtype=np.float32).tobytes()

    @staticmethod
    def from_bytes(blob):
        """Convert binary blob back to float list."""
        return np.frombuffer(blob, dtype=np.float32).tolist()
