# PythonAnywhere WSGI Entrypoint with Error Logging

import sys
import os
import traceback

# Add project root directory to sys.path
project_folder = os.path.dirname(os.path.abspath(__file__))
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

# Set UTF-8 encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from a2wsgi import WSGIMiddleware
    from ui.web_dashboard import app

    application = WSGIMiddleware(app)
    print("Successfully initialized FastAPI WSGIMiddleware for PythonAnywhere!")
except Exception as e:
    print(f"WSGI Initialization Error: {e}")
    traceback.print_exc()
    raise e
