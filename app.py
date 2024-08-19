#!/usr/bin/python3
#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
import os

os.environ["TINA4_DEFAULT_WEBSERVER"] = "False"

from tina4_python import *

Debug("Running the service")
run_web_server("0.0.0.0", 7180)
