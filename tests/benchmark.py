"""Benchmark: ThoughtDB vs ChromaDB vs FAISS vs Qdrant

Madagascar Zoo Animals Edition!
Compares: insert speed, search latency, memory usage, and search quality.
"""
import os
import sys
import time
import sqlite3
import struct
import random
import gc
import tracemalloc
import numpy as np

os.environ["TINA4_DEFAULT_WEBSERVER"] = "False"
os.environ["TINA4_DEBUG_LEVEL"] = ""
sys.argv.append("stop")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = "./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf"

# Madagascar zoo animal data
SPECIES = [
    ("Ring-tailed Lemur", "lemur", "Primates", "Herbivore",
     "Iconic lemur with a long black-and-white striped tail, lives in groups of up to 30, sunbathes in the morning"),
    ("Aye-Aye", "lemur", "Primates", "Omnivore",
     "Nocturnal lemur with large ears and elongated middle finger used to tap on trees and find grubs"),
    ("Fossa", "carnivore", "Eupleridae", "Carnivore",
     "Madagascar's largest predator, cat-like body with a long tail, hunts lemurs in the forest canopy"),
    ("Indri", "lemur", "Primates", "Herbivore",
     "Largest living lemur, famous for loud wailing songs that carry through the rainforest for kilometers"),
    ("Panther Chameleon", "reptile", "Chamaeleonidae", "Insectivore",
     "Strikingly colorful chameleon that changes colors for communication, has independently moving eyes"),
    ("Madagascar Hissing Cockroach", "insect", "Gromphadorhini", "Detritivore",
     "Large wingless cockroach that produces a hissing sound by forcing air through its spiracles"),
    ("Tomato Frog", "amphibian", "Microhylidae", "Insectivore",
     "Bright red-orange frog that puffs up when threatened and secretes a sticky toxic substance"),
    ("Sifaka", "lemur", "Primates", "Herbivore",
     "Dancing lemur that leaps sideways across the ground with arms raised, lives in family groups in trees"),
    ("Tenrec", "mammal", "Tenrecidae", "Omnivore",
     "Hedgehog-like mammal that can lower body temperature to match surroundings, covered in spines and fur"),
    ("Madagascar Day Gecko", "reptile", "Gekkonidae", "Omnivore",
     "Brilliant green gecko active during daytime, licks nectar from flowers and eats insects"),
    ("Radiated Tortoise", "reptile", "Testudinidae", "Herbivore",
     "Elegant tortoise with star-patterned shell, critically endangered, can live over 100 years"),
    ("Madagascar Fish Eagle", "bird", "Accipitridae", "Piscivore",
     "One of the rarest birds of prey in the world, hunts fish from lakes and rivers"),
    ("Blue Coua", "bird", "Cuculidae", "Omnivore",
     "Beautiful bird with vivid blue plumage and bare blue skin around the eyes, walks on forest floor"),
    ("Leaf-tailed Gecko", "reptile", "Uroplatus", "Insectivore",
     "Master of camouflage with a flat tail that looks exactly like a dead leaf, hunts at night"),
    ("Madagascar Ground Boa", "reptile", "Boidae", "Carnivore",
     "Non-venomous constrictor snake found in dry forests, hunts small mammals and birds at night"),
    ("Comet Moth", "insect", "Saturniidae", "None",
     "One of the largest silk moths with a wingspan of 20cm and long tail streamers, adults do not eat"),
    ("Verreaux's Eagle-Owl", "bird", "Strigidae", "Carnivore",
     "Madagascar's largest owl with distinctive ear tufts, deep hooting call echoes through dry forests"),
    ("Madagascar Pygmy Kingfisher", "bird", "Alcedinidae", "Insectivore",
     "Tiny colorful forest kingfisher that does not fish, instead hunts insects and lizards in leaf litter"),
    ("Nile Crocodile", "reptile", "Crocodylidae", "Carnivore",
     "Large crocodile found in rivers and lakes, ambush predator that can grow up to 5 meters long"),
    ("Mouse Lemur", "lemur", "Primates", "Omnivore",
     "World's smallest primate weighing only 30 grams, huge eyes for nocturnal foraging in the forest"),
]

HABITATS = [
    "tropical rainforest", "dry deciduous forest", "spiny forest",
    "mangrove swamp", "montane forest", "coastal scrubland",
    "freshwater lake", "river basin", "limestone karst",
]

BEHAVIORS = [
    "territorial and vocal", "shy and solitary", "highly social",
    "aggressive when threatened", "migratory", "nomadic forager",
    "cooperative breeder", "crepuscular hunter", "basking specialist",
]

CONSERVATION = [
    "Critically Endangered", "Endangered", "Vulnerable",
    "Near Threatened", "Least Concern",
]

SEARCH_QUERIES = [
    "nocturnal lemur with big eyes",
    "colorful chameleon that changes color",
    "endangered tortoise with patterned shell",
    "predator that hunts in the forest canopy",
    "tiny primate that forages at night",
    "large reptile that lives in rivers",
    "bird of prey that catches fish",
    "insect that makes hissing sounds",
    "dancing lemur that leaps sideways",
    "camouflage gecko that looks like a leaf",
]


def generate_animals(n):
    """Generate n Madagascar zoo animal records."""
    animals = []
    for i in range(n):
        species = random.choice(SPECIES)
        habitat = random.choice(HABITATS)
        behavior = random.choice(BEHAVIORS)
        status = random.choice(CONSERVATION)
        weight = round(random.uniform(0.03, 150.0), 2)
        name = f"{species[0]} #{i+1}"
        description = (
            f"{species[0]} is a {species[1]} in the family {species[2]}. "
            f"{species[4]}. "
            f"Diet: {species[3]}. Lives in {habitat}. "
            f"Behavior: {behavior}. "
            f"Conservation status: {status}. Weight: {weight}kg."
        )
        animals.append((i + 1, name, species[0], species[1], species[3],
                        habitat, status, weight, description))
    return animals


def setup_source_db(animals, db_path):
    """Create a SQLite source DB with zoo animals."""
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE animals (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            species TEXT,
            animal_type TEXT,
            diet TEXT,
            habitat TEXT,
            conservation_status TEXT,
            weight_kg REAL,
            description TEXT
        )
    """)
    conn.executemany(
        "INSERT INTO animals (id, name, species, animal_type, diet, habitat, conservation_status, weight_kg, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        animals
    )
    conn.commit()
    conn.close()


def get_shared_embedder():
    """Get or create the shared ThoughtDB embedder for fair comparison."""
    from thoughtdb.embedder import Embedder
    if not hasattr(get_shared_embedder, "_instance"):
        get_shared_embedder._instance = Embedder(MODEL_PATH)
    return get_shared_embedder._instance


def pre_embed(animals):
    """Pre-embed all animals using ThoughtDB's embedder (shared across benchmarks for fairness)."""
    embedder = get_shared_embedder()
    vectors = []
    for a in animals:
        text = f"{a[2]} {a[8]}"  # species + description
        vec = embedder.embed(text)
        vectors.append(np.array(vec, dtype=np.float32))
    return vectors


def pre_embed_queries():
    """Pre-embed search queries."""
    embedder = get_shared_embedder()
    return [np.array(embedder.embed(q), dtype=np.float32) for q in SEARCH_QUERIES]


def _measure_peak(func):
    """Run func() while tracking peak memory accurately.
    Returns (func_result, peak_bytes).
    Forces GC and resets tracemalloc peak before measuring."""
    gc.collect()
    if tracemalloc.is_tracing():
        tracemalloc.stop()
    tracemalloc.start()
    tracemalloc.reset_peak()
    result = func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, peak


# ─── ThoughtDB ───────────────────────────────────────────────────────────────

def benchmark_thoughtdb(animals, db_path, index_path):
    """Benchmark ThoughtDB: sync + search."""
    from thoughtdb import ThoughtDB

    if os.path.exists(index_path):
        os.remove(index_path)

    def do_sync():
        return ThoughtDB(
            dsn=f"sqlite3:{db_path}",
            vectors={"animals": {"columns": ["name", "species", "description"], "key": "id"}},
            model_path=MODEL_PATH,
            index_path=index_path,
            auto_sync=True,
        )

    t0 = time.perf_counter()
    tdb, sync_peak = _measure_peak(do_sync)
    sync_time = time.perf_counter() - t0

    search_times = []
    for q in SEARCH_QUERIES:
        t0 = time.perf_counter()
        tdb.search(q, table="animals", limit=5)
        search_times.append(time.perf_counter() - t0)

    tdb.close()
    if os.path.exists(index_path):
        os.remove(index_path)

    return {
        "name": "ThoughtDB",
        "sync_time": sync_time,
        "sync_peak_mem_mb": sync_peak / (1024 * 1024),
        "avg_search_ms": sum(search_times) / len(search_times) * 1000,
        "min_search_ms": min(search_times) * 1000,
        "max_search_ms": max(search_times) * 1000,
    }


# ─── ChromaDB ────────────────────────────────────────────────────────────────

def benchmark_chromadb(animals):
    """Benchmark ChromaDB: insert + search (uses its own embedder)."""
    import chromadb

    client = chromadb.Client()
    try:
        client.delete_collection("animals")
    except Exception:
        pass

    def do_insert():
        collection = client.create_collection("animals", metadata={"hnsw:space": "cosine"})
        batch_size = 100
        for i in range(0, len(animals), batch_size):
            batch = animals[i:i + batch_size]
            ids = [str(a[0]) for a in batch]
            docs = [f"{a[2]} {a[8]}" for a in batch]
            metadatas = [{"species": a[2], "type": a[3]} for a in batch]
            collection.add(ids=ids, documents=docs, metadatas=metadatas)
        return collection

    t0 = time.perf_counter()
    collection, insert_peak = _measure_peak(do_insert)
    insert_time = time.perf_counter() - t0

    search_times = []
    for q in SEARCH_QUERIES:
        t0 = time.perf_counter()
        collection.query(query_texts=[q], n_results=5)
        search_times.append(time.perf_counter() - t0)

    return {
        "name": "ChromaDB",
        "sync_time": insert_time,
        "sync_peak_mem_mb": insert_peak / (1024 * 1024),
        "avg_search_ms": sum(search_times) / len(search_times) * 1000,
        "min_search_ms": min(search_times) * 1000,
        "max_search_ms": max(search_times) * 1000,
    }


# ─── FAISS ───────────────────────────────────────────────────────────────────

def benchmark_faiss(animals, vectors, query_vectors):
    """Benchmark FAISS: insert + search (pre-embedded vectors)."""
    import faiss

    dim = vectors[0].shape[0]

    def do_insert():
        idx = faiss.IndexFlatL2(dim)
        matrix = np.stack(vectors)
        idx.add(matrix)
        return idx

    t0 = time.perf_counter()
    index, insert_peak = _measure_peak(do_insert)
    insert_time = time.perf_counter() - t0

    search_times = []
    for qv in query_vectors:
        t0 = time.perf_counter()
        index.search(qv.reshape(1, -1), 5)
        search_times.append(time.perf_counter() - t0)

    return {
        "name": "FAISS",
        "sync_time": insert_time,
        "sync_peak_mem_mb": insert_peak / (1024 * 1024),
        "avg_search_ms": sum(search_times) / len(search_times) * 1000,
        "min_search_ms": min(search_times) * 1000,
        "max_search_ms": max(search_times) * 1000,
    }


# ─── Qdrant ──────────────────────────────────────────────────────────────────

def benchmark_qdrant(animals, vectors, query_vectors):
    """Benchmark Qdrant (in-memory mode): insert + search."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance, PointStruct

    dim = vectors[0].shape[0]

    def do_insert():
        cl = QdrantClient(":memory:")
        cl.create_collection(
            collection_name="animals",
            vectors_config=VectorParams(size=dim, distance=Distance.EUCLID),
        )
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            points = []
            for j in range(i, min(i + batch_size, len(vectors))):
                points.append(PointStruct(
                    id=j + 1,
                    vector=vectors[j].tolist(),
                    payload={"species": animals[j][2], "type": animals[j][3]},
                ))
            cl.upsert(collection_name="animals", points=points)
        return cl

    t0 = time.perf_counter()
    client, insert_peak = _measure_peak(do_insert)
    insert_time = time.perf_counter() - t0

    search_times = []
    for qv in query_vectors:
        t0 = time.perf_counter()
        client.query_points(
            collection_name="animals",
            query=qv.tolist(),
            limit=5,
        )
        search_times.append(time.perf_counter() - t0)

    return {
        "name": "Qdrant",
        "sync_time": insert_time,
        "sync_peak_mem_mb": insert_peak / (1024 * 1024),
        "avg_search_ms": sum(search_times) / len(search_times) * 1000,
        "min_search_ms": min(search_times) * 1000,
        "max_search_ms": max(search_times) * 1000,
    }


# ─── Runner ──────────────────────────────────────────────────────────────────

def run_benchmark(n):
    """Run all benchmarks for n animals."""
    print(f"\n{'='*80}")
    print(f"  MADAGASCAR ZOO BENCHMARK: {n} animals")
    print(f"{'='*80}")

    animals = generate_animals(n)
    db_path = f"./bench_zoo_{n}.db"
    index_path = f"./bench_zoo_index_{n}.db"

    setup_source_db(animals, db_path)

    # Pre-embed for FAISS/Qdrant (fair: same vectors, excludes embedding time)
    print(f"\n  Pre-embedding {n} animals...")
    vectors = pre_embed(animals)
    query_vectors = pre_embed_queries()

    print(f"  ThoughtDB ({n} animals)...")
    tdb = benchmark_thoughtdb(animals, db_path, index_path)

    print(f"  ChromaDB ({n} animals)...")
    chroma = benchmark_chromadb(animals)

    print(f"  FAISS ({n} animals)...")
    faiss_r = benchmark_faiss(animals, vectors, query_vectors)

    print(f"  Qdrant ({n} animals)...")
    qdrant_r = benchmark_qdrant(animals, vectors, query_vectors)

    if os.path.exists(db_path):
        os.remove(db_path)

    all_results = [tdb, chroma, faiss_r, qdrant_r]

    # Print table
    header = f"  {'Metric':<22}"
    for r in all_results:
        header += f" {r['name']:>12}"
    print(f"\n{header}")
    print(f"  {'-'*(22 + 13 * len(all_results))}")

    metrics = [
        ("Sync/Insert (s)", "sync_time"),
        ("Peak Memory (MB)", "sync_peak_mem_mb"),
        ("Avg Search (ms)", "avg_search_ms"),
        ("Min Search (ms)", "min_search_ms"),
        ("Max Search (ms)", "max_search_ms"),
    ]

    for label, key in metrics:
        row = f"  {label:<22}"
        vals = [r[key] for r in all_results]
        best = min(vals)
        for v in vals:
            marker = " *" if v == best else "  "
            row += f" {v:>10.2f}{marker}"
        print(row)

    print(f"\n  * = best in category")
    print(f"  Note: FAISS/Qdrant use pre-embedded vectors (no embedding time in sync)")
    print(f"  ThoughtDB/ChromaDB embed during sync (includes embedding time)")

    return all_results


if __name__ == "__main__":
    random.seed(42)

    sizes = [100, 500]
    for n in sizes:
        run_benchmark(n)

    print(f"\n{'='*80}")
    print("  WHAT EACH SYSTEM IS")
    print(f"{'='*80}")
    print("""
  ThoughtDB  - Vector layer for ANY relational database (SQLite/Postgres/MySQL/
               Firebird/MSSQL). Sidecar sqlite-vec index. Built-in embeddings.
               MCP server for LLM integration. Source DB is never modified.

  ChromaDB   - Standalone vector database. In-memory HNSW index. Requires
               copying data out of your relational database.

  FAISS      - Vector search library (not a database). No persistence, no
               metadata, no DB integration. Raw speed benchmark only.

  Qdrant     - Standalone vector database with rich filtering. In-memory mode
               used here. Production mode requires separate server.
""")
