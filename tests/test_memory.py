#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from time import perf_counter as pc
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR + "/../thoughtdb"))

from thoughtdb.Collection import Collection
from thoughtdb.Organization import Organization
from thoughtdb.VectorStore import VectorStore
from thoughtdb.Memory import Memory

if os.path.isfile('./tests/test2.db'):
    os.remove("./tests/test2.db")
vector_store = VectorStore("sqlite3:tests/test2.db")
memory = Memory(vector_store)
list_of_items = ["Red", "Angry", "Mouse", "Ant", "Eat", "Sleep", "Cow", "Thought", "Black", "Apple", "Sheep", "Orange",
                 "Spoon", "Woman", "Merry-go-round", "Horse", "Pig", "Arrow", "Door", "Car", "Boat", "Bicycle", "Bow",
                 "Happiness"]


def test_memory():
    counter = 0
    for item in list_of_items:
        counter += 1
        vectors = vector_store.embedder.embed(item)
        memory.add_embedding(counter, vectors)


def test_vector_search():
    start = pc()
    # sql query to find ids from the collection
    search = memory.search("I want to feed", 20, [3, 4, 6])
    for result in search:
        print(list_of_items[result["id"] - 1], str(result["match"]) + "%")
    end = pc()

    print("Time:", end - start)

    assert search == [{'id': 4, 'match': 48}, {'id': 3, 'match': 46}, {'id': 6, 'match': 44}]


def test_embedding_data():
    counter = 1
    for item in list_of_items:
        vector_store.database.insert("document", {"name": "document" + str(counter), "data": item,
                                                  "meta": {"id": counter, "type": item}})
        vector_store.database.commit()
        counter += 1
    # table_name, column_name, key_name, key_value
    results = vector_store.database.fetch(
        "select id, embed('document', 'data', 'id', d.id, d.data) as embed from document d", limit=100)
    vector_store.database.commit()


def test_searching_data():
    results = vector_store.database.fetch(
        "select id, name, data, score('document', 'data', 'id', d.id, 'farm animals') as score from document d order by 4 desc ", limit=100)
    vector_store.database.commit()
    assert results.records[0] == {'id': 7, 'name': 'document7', 'data': 'Cow', 'score': 74}
    results = vector_store.database.fetch("select * from search('vehicles')")
    assert results.records == []


