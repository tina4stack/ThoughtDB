#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from time import perf_counter as pc
import os
import sys

from thoughtdb.Memory import Memory

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR + "/../thoughtdb"))

from thoughtdb.Collection import Collection
from thoughtdb.Organization import Organization
from thoughtdb.VectorStore import VectorStore

if os.path.isfile('./tests/test.db'):
    os.remove("./tests/test.db")
vector_store = VectorStore("sqlite3:tests/test.db")
memory = Memory(vector_store)
list_of_items = ["Red", "Angry", "Mouse", "Ant", "Eat", "Sleep", "Cow", "Thought", "Black",  "Apple", "Sheep", "Orange", "Spoon", "Woman", "Merry-go-round", "Horse", "Pig", "Arrow", "Door", "Car", "Boat", "Bicycle", "Bow", "Happiness"]


def test_memory():
    counter = 0
    for item in list_of_items:
        counter += 1
        vectors = vector_store.embedder.embed(item)
        memory.add_embedding(counter, vectors)

def test_vector_search():
    start = pc()
    search = memory.search("I want to feed", 20)
    for result in search:
        print(list_of_items[result["id"]-1], str(result["match"])+"%" )
    end = pc()

    print("Time:", end-start)


    assert search is None

