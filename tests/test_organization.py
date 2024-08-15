#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import os
import sys
import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR + "/../thoughtdb"))

from thoughtdb.Collection import Collection
from thoughtdb.Organization import Organization
from thoughtdb.VectorStore import VectorStore

if os.path.isfile('./tests/test.db'):
    os.remove("./tests/test.db")
vector_store = VectorStore("sqlite3:tests/test.db")


def test_dba_clean():
    vector_store.database.execute("delete from system.organization where id <> 0")
    vector_store.database.commit()


def test_dba_vector():
    vec_version = vector_store.database.fetch("select vec_version()")
    if os.name == 'nt':
        assert vec_version[0] == {"vec_version()": "v0.0.1-alpha.19"}
    else:
        assert vec_version[0] == {"vec_version()": "v0.1.1"}

def test_vector_store_embedder():
    embeddings = vector_store.embedder.embed("Text")
    assert len(embeddings) == 768

def test_vector_store_functionality():
    organisations = vector_store.get_organizations()
    assert organisations == {}
    with pytest.raises(Exception):
        organisations = vector_store.get_organizations("cooking")
    cooking = vector_store.get_organization("cooking", create=True)
    pots = cooking.get_collection("pots", create=True)
    organisations = vector_store.get_organizations()
    assert organisations["cooking"].data["name"] == "cooking"


def test_create_organization():
    organization = Organization(vector_store)
    assert organization is not None
    org1 = organization.create("one")
    assert org1.data["id"] == 2
    org2 = organization.create("two")
    assert org2.data["id"] == 3


def test_update_organization():
    organization = Organization(vector_store)
    assert organization is not None
    update_one = organization.update("one_update", 2)
    assert "oneupdate" == update_one.data["name"]
    update_one = organization.update("one_update!", 2)
    assert "oneupdate" == update_one.data["name"]


def test_delete_organization():
    organization = Organization(vector_store)
    assert organization is not None
    del1 = organization.delete("oneupdate")
    assert del1.data is None
    organization.delete(id=3)


def test_general_functionality():
    organization = Organization(vector_store)
    with pytest.raises(Exception):
        organization.load("testing")
    with pytest.raises(Exception):
        collection = organization.get_collections("collectiona")

    organization.load("cooking")
    assert organization.data["name"] == "cooking"
    collection = organization.get_collection("pans", create=True)

    with pytest.raises(Exception):
        collection.get_document("meemee")

    moomoo_document = collection.get_document("moomoo", create=True)
    moomoo_conversation =  collection.get_conversation("moomoo", create=True)

    moomoo_document.update(data="The clock within this blog and the clock on my laptop are 1 hour different from each other. If you spin around three times, you'll start to feel melancholy.", metadata={"hello": "world", "revision":"1.0"})

    moo2 = collection.get_document("moomoo", create=False)
    print(moo2.data)

    moomoo_document.append(data="The beach was crowded with snow leopards. You're good at English when you know the difference between a man eating chicken and a man-eating chicken.", metadata={"chickens": "world", "revision": "2.0"})

    moo3 = collection.get_document("moomoo", create=False)
    print(moo3.data)