# PythonAnywhere WSGI Entrypoint
# ASGIMiddleware converts FastAPI (ASGI) to PythonAnywhere (WSGI)

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
    from a2wsgi import ASGIMiddleware
    from ui.web_dashboard import app

    # ASGIMiddleware wraps FastAPI (ASGI) into WSGI for PythonAnywhere
    application = ASGIMiddleware(app)
    print("Successfully initialized FastAPI ASGIMiddleware for PythonAnywhere!")
except Exception as e:
    print(f"WSGI Initialization Error: {e}")
    traceback.print_exc()
    raise e
