# PythonAnywhere WSGI Entrypoint for FastAPI

import sys
import os
import traceback

# Add project root directory to sys.path
project_folder = os.path.dirname(os.path.abspath(__file__))
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from a2wsgi import ASGIMiddleware
    from ui.web_dashboard import app

    # ASGIMiddleware with wait_time optimized for PythonAnywhere WSGI server
    application = ASGIMiddleware(app, wait_time=0.001)
    print("FastAPI ASGIMiddleware successfully loaded!")
except Exception as e:
    print(f"WSGI Entrypoint Exception: {e}")
    traceback.print_exc()
    raise e
