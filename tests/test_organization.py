#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR + "/../thoughtdb"))

from thoughtdb.app.Organization import Organization
from thoughtdb.app.VectorStore import VectorStore
os.remove("tests/test.db")
vector_store = VectorStore("sqlite3:tests/test.db")


def test_dba_clean():
    vector_store.dba.execute("delete from organization where id <> 0")
    vector_store.dba.commit()


def test_dba_vector():
    vec_version = vector_store.dba.fetch("select vec_version()")
    print(vec_version)
    assert vec_version[0] == {"vec_version()": "v0.1.1"}


def test_create_organization():
    organization = Organization(vector_store)
    assert organization is not None
    org1 = organization.create("one")
    assert org1.id == 1
    org2 = organization.create("two")
    assert org2.id == 2


def test_update_organization():
    organization = Organization(vector_store)
    assert organization is not None
    update_one = organization.update("one_update", 1)
    assert "oneupdate" == update_one.data["name"]
    update_one = organization.update("one_update!", 1)
    assert "oneupdate" == update_one.data["name"]


def test_delete_organization():
    organization = Organization(vector_store)
    assert organization is not None
    del1 = organization.delete("oneupdate")
    assert del1.data == None
    organization.delete(id=2)
