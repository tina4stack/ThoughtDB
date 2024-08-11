#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import sqlite_vec
from tina4_python.Database import Database
from tina4_python import Migration


class VectorStore:

    def __init__(self, path):
        self.dba = Database(path, "", "")
        Migration.migrate(self.dba)
        self.dba.dba.enable_load_extension(True)
        sqlite_vec.load(self.dba.dba)
        self.dba.dba.enable_load_extension(False)
