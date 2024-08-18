# Start your project here
import os
import shutil
os.environ["TINA4_DEFAULT_WEBSERVER"] = "False"

thought_db_library_path = os.path.dirname(os.path.realpath(__file__))
thought_db_root_path = os.path.realpath(os.getcwd())

# Hack for local development
if os.getenv('THOUGHT_DB_DEV_MODE'):
    thought_db_root_path = thought_db_root_path.split("thoughtdb")[0]

source_dir = thought_db_library_path + os.sep + "migrations"
destination_dir = thought_db_root_path + os.sep + "migrations"
shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

if not os.path.exists(thought_db_root_path + os.sep + "database"):
    source_dir = thought_db_library_path + os.sep + "database"
    destination_dir = thought_db_root_path + os.sep + "database"
    shutil.copytree(source_dir, destination_dir)

if not os.path.exists(thought_db_root_path + os.sep + "models_db"):
    source_dir = thought_db_library_path + os.sep + "models_db"
    destination_dir = thought_db_root_path + os.sep + "models_db"
    shutil.copytree(source_dir, destination_dir)

if not os.path.isfile(thought_db_root_path + os.sep + "app.py"):
    source_dir = thought_db_library_path + os.sep + "app.sample"
    destination_dir = thought_db_root_path + os.sep + "app.py"
    shutil.copy(source_dir, destination_dir)

# @todo put back
#source_dir = thought_db_library_path + os.sep + "routes" + os.sep + "api.py"
#destination_dir = thought_db_root_path + os.sep + "src" + os.sep + "routes" + os.sep + "thought_db_api.py"
#shutil.copy(source_dir, destination_dir)

if not os.path.isfile(thought_db_root_path + os.sep + ".env"):
    source_dir = thought_db_library_path + os.sep + ".env.sample"
    destination_dir = thought_db_root_path + os.sep + ".env"
    shutil.copy(source_dir, destination_dir)
