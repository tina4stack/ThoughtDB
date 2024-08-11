# Start your project here
import os
import shutil
os.environ["TINA4_DEFAULT_WEBSERVER"] = "False"

thoughtdb_library_path = os.path.dirname(os.path.realpath(__file__))
thoughtdb_root_path = os.path.realpath(os.getcwd())

# Hack for local development
if os.getenv('THOUGHTDB_DEV_MODE'):
    thoughtdb_root_path = thoughtdb_root_path.split("thoughtdb")[0][:-1]

source_dir = thoughtdb_library_path + os.sep + "migrations"
destination_dir = thoughtdb_root_path + os.sep + "migrations"
shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

if not os.path.exists(thoughtdb_root_path + os.sep + "database"):
    source_dir = thoughtdb_library_path + os.sep + "database"
    destination_dir = thoughtdb_root_path + os.sep + "database"
    shutil.copytree(source_dir, destination_dir)

if not os.path.exists(thoughtdb_root_path + os.sep + "models_db"):
    source_dir = thoughtdb_library_path + os.sep + "models_db"
    destination_dir = thoughtdb_root_path + os.sep + "models_db"
    shutil.copytree(source_dir, destination_dir)

if not os.path.isfile(thoughtdb_root_path + os.sep + "app.py"):
    source_dir = thoughtdb_library_path + os.sep + "app.sample"
    destination_dir = thoughtdb_root_path + os.sep + "app.py"
    shutil.copy(source_dir, destination_dir)

if not os.path.isfile(thoughtdb_root_path + os.sep + ".env"):
    source_dir = thoughtdb_library_path + os.sep + ".env.sample"
    destination_dir = thoughtdb_root_path + os.sep + ".env"
    shutil.copy(source_dir, destination_dir)
