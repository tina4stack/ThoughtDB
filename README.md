# ThoughtDB
ThoughtDB is a mix between relational and vector database for efficient data retrieval

## Installation

### Windows
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install poetry
```

### MacOS / Linux
```bash
python3 -m venv .venv
source ./.venv/bin/activate
pip install poetry
```

```bash
poetry run python app.py 0.0.0.0:8003
```

### Text Embedding Models

Download the following model or model of your choice in GGUF format into the models_db folder
```bash
https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf?download=true
```

# Data Structure

The following is the layout for the ThoughtDB data structure. As we are in Alpha phase this structure may change as we optimize things. 

- Organizations
  - Collections
    - Conversations
      - Sessions
      - History
      - Summaries
    - Document Types
      - Documents
        - Chapters
        - Paragraphs
        - Sentences
        - Words

# Overview

## Installing

Installation should be simple

### Pip
```bash
pip install thoughtdb
```

### Poetry
```bash
poetry add thoughtdb
```

## Creating a new database

Currently, we only support Sqlite3, all the dependencies should be installed by pip or poetry.

```python
from thoughtdb.src.app import VectorStore


```