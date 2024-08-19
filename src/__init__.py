# Start your project here
import os
from thoughtdb.VectorStore import VectorStore

vector_store = VectorStore("sqlite3:" + os.getenv("DATABASE"))

import src.routes.thought_db_api

