# PythonAnywhere WSGI Entrypoint
# PythonAnywhere uses WSGI. We wrap our FastAPI app using a2wsgi.

import sys
import os

# Path to project directory
project_folder = os.path.dirname(os.path.abspath(__file__))
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

try:
    from a2wsgi import WSGIMiddleware
    from ui.web_dashboard import app
    
    application = WSGIMiddleware(app)
except ImportError:
    from ui.web_dashboard import app as application
