# Start your project here
import os

from tina4_python import Migration
from tina4_python.Database import Database

dba = Database("sqlite3:"+os.getenv("DATABASE"), "", "")
Migration.migrate(dba)