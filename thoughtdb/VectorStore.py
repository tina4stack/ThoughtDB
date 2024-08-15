#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import os
import sqlite_vec
from tina4_python.Database import Database
from tina4_python import Migration

from thoughtdb.Core import Core
from thoughtdb.Organization import Organization
from thought.model_loader import load_model


class VectorStore(Core):

    def __init__(self, path, model_path="./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf", embedder=None):
        """
        Initializes the vector store
        :param path:
        """
        self.database = Database(path, "", "")
        Migration.migrate(self.database)
        self.database.dba.enable_load_extension(True)

        try:
            if os.name == 'nt':
                self.database.dba.load_extension(os.path.dirname(os.path.realpath(__file__))+os.sep+"vec0.dll")
            else:
                sqlite_vec.load(self.database.dba)
        except Exception as e:
            print("Could not load vector module for SQLite")

        # @todo load embeddings into memory and spin off an encoding thread to embed data
        if embedder is None:
            embedder = load_model (model_path, verbose=True, embedding=True)


        self.embedder = embedder
        self.database.dba.enable_load_extension(False)
        self.model_path=model_path
        self._organizations = {}
        super(VectorStore, self).__init__(self)
    
    def get_organizations(self, name="", raise_exception=True):
        return self.get_basic_dataset(name, self._organizations, Organization, "organization", filter="id <> 0", raise_exception=raise_exception)

    def get_organization(self, name, create=False):
        organization = self.get_organizations(name, False)
        if organization == {} and create:
            organization = Organization(self)
            organization.create(name)
        else:
            raise Exception(f"No organization found with name {name}")
        return organization

    def run_embedding_thread(self, on_complete=None, keep_running=False):
        pass

