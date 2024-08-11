# Start your project here
import os
from .app.VectorStore import VectorStore

vector_store = VectorStore("sqlite3:"+os.getenv("DATABASE"))
