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

os.remove("tests/test.db")
vector_store = VectorStore("sqlite3:tests/test.db")


def test_dba_clean():
    vector_store.database.execute("delete from organization where id <> 0")
    vector_store.database.commit()


def test_dba_vector():
    vec_version = vector_store.database.fetch("select vec_version()")
    print(vec_version)
    assert vec_version[0] == {"vec_version()": "v0.1.1"}


def test_vector_store_functionality():
    organisations = vector_store.get_organizations()
    assert organisations is None
    with pytest.raises(Exception):
        organisations = vector_store.get_organizations("cooking")
    cooking = vector_store.get_organization("cooking", create=True)
    pots = cooking.get_collection("pots", create=True)


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
    assert del1.data == None
    organization.delete(id=3)


def test_general_functionality():
    organization = Organization(vector_store)
    organization.load("testing")
    with pytest.raises(Exception):
        collection = organization.get_collections("collectiona")
    collection = organization.get_collection("pans", create=True)
    collection.get_document("moomoo", create=True)
    collection.get_conversation("moomoo", create=True)