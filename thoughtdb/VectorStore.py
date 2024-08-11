#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import sqlite_vec
from tina4_python.Database import Database
from tina4_python import Migration

from thoughtdb.Core import Core
from thoughtdb.Organization import Organization


class VectorStore(Core):

    def __init__(self, path, model_path="./nomic-embed-text-v1.5.Q4_K_M.gguf"):
        """
        Initializes the vector store
        :param path:
        """
        self.database = Database(path, "", "")
        Migration.migrate(self.database)
        self.database.dba.enable_load_extension(True)
        sqlite_vec.load(self.database.dba)
        self.database.dba.enable_load_extension(False)
        self.model_path=model_path
        self._organizations = None
        super(VectorStore, self).__init__(self)
    
    def get_organizations(self, name="", raise_exception=True):
        return self.get_basic_dataset(name, self._organizations, Organization, "organization", filter="id <> 0", raise_exception=raise_exception)

    def get_organization(self, name, create=False):
        organization = self.get_organizations(name, False)
        if organization is None and create:
            organization = Organization(self)
            organization.create(name)

        return organization

