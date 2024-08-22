#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import os
import json
import threading

import sqlite_vec
from tina4_python.Database import Database
from tina4_python import Migration
from watchdog.observers import Observer

from thoughtdb.Core import Core
from thoughtdb.Memory import Memory
from thoughtdb.Organization import Organization
from thought.model_loader import load_model
from tina4_python import Debug, Constant


class VectorStore(Core):

    def __init__(self, path, model_path="./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf", embedder=None,
                 data_increments=1000):
        """
        Initializes the vector store
        :param path:
        """
        self.database = Database(path, "", "")
        Migration.migrate(self.database)
        self.database.dba.enable_load_extension(True)
        self.memory = Memory(self)
        self.last_embedding_search = None
        self.last_embedding = None
        self.data_increments = data_increments

        try:
            if os.name == 'nt':
                self.database.dba.load_extension(os.path.dirname(os.path.realpath(__file__)) + os.sep + "vec0.dll")
            else:
                sqlite_vec.load(self.database.dba)
        except Exception as e:
            print("Could not load vector module for SQLite")

        # @todo load embeddings into memory and spin off an encoding thread to embed data
        #self.embed_load_thread = threading.Thread(target=self.load_embeddings_to_memory, args=(self.memory,), daemon=True)
        #self.embed_load_thread.start()
        self.load_embeddings_to_memory(self.memory)

        if embedder is None:
            embedder = load_model(model_path, verbose=True, embedding=True)

        self.database.dba.create_function("embed", 5, self.create_embedding)
        self.database.dba.create_function("score", 5, self.vector_score)
        self.database.dba.create_function("search", 2, self.search)
        self.embedder = embedder
        self.database.dba.enable_load_extension(False)
        self.model_path = model_path
        self.model_name = model_path.split("/")[-1]
        self._organizations = {}
        super(VectorStore, self).__init__(self)

    def get_organizations(self, name="", id=0, raise_exception=True):
        """
        Get organizations from the vector store
        :param id:
        :param name:
        :param raise_exception:
        :return:
        """
        return self.get_basic_dataset(self.system_name(name), self._organizations, Organization,
                                      "organization", id=id, filter="id <> 0",
                                      raise_exception=raise_exception)

    def get_organization(self, name="", id=0, create=False):
        """
        Gets a single organization from the vector store
        :param id:
        :param name:
        :param create:
        :return:
        """
        organization = self.get_organizations(name, id=id, raise_exception=False)

        if organization == {} and create:
            organization = Organization(self)
            organization.create(name)
        else:
            if organization == {}:
                raise Exception(f"No organization found: {name} {id}")

        return organization

    def del_organization(self, name="", id=0):
        return self._delete(name=name, id=id, data_name="organization")

    def create_embedding(self, table_name, column_name, key_name, key_value, data):
        """
        Embeds a value into the database based on the values
        :param data:
        :param table_name:
        :param column_name:
        :param key_name:
        :param key_value:
        :return:
        """
        if data is None:
            return ""

        data = self.embedder.embed(data)

        self.database.insert("embedding", {"table_name": table_name, "column_name": column_name, "key_name": key_name,
                                           "key_value": key_value, "model_name": self.model_name, "data": data})
        self.database.commit()
        return json.dumps(data)

    def vector_score(self, table_name, column_name, key_name, key_value, search):
        """
        Returns back the score based on the search
        :param table_name:
        :param column_name:
        :param key_name:
        :param key_value:
        :param search
        :return:
        """
        score = 0
        try:
            if self.last_embedding_search != search:
                self.last_embedding = self.embedder.embed(search)
                self.last_embedding_search = search

            record = self.database.fetch_one(
                "select data from embedding where table_name = ? and column_name = ? and key_name = ? and key_value = ?",
                [table_name, column_name, key_name, key_value])
            if record is None:
                return 0

            score = Memory.get_distance(self.last_embedding, record["data"])
        except Exception as e:
            pass
        return score

    def search(self, search, count=5):
        """
        Search the embedding table
        :param count:
        :param search:
        :return:
        """
        results = self.memory.search(search, count)
        ids = []
        for result in results:
            ids.append(result["id"])

        return json.dumps(ids)

    def load_embeddings_to_memory(self, memory):
        Debug("Start loading embeddings", Constant.TINA4_LOG_DEBUG)
        count = 0
        data = self.database.fetch("select id, data from embedding order by id", limit=self.data_increments, skip=count)
        while len(data.records) > 0:
            for record in data.records:
                memory.add_embedding(record["id"], record["data"])
            count += self.data_increments
            print("Fetching next ", self.data_increments)
            data = self.database.fetch("select * from embedding order by id", limit=self.data_increments, skip=count)
        Debug("Done loading embeddings", Constant.TINA4_LOG_DEBUG)

    def run_embedding_thread(self, on_complete=None, keep_running=False):
        pass


