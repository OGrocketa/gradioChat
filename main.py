import os
import shutil

from gradio_ui.ui import create_ui

try:
    demo = create_ui()
    demo.launch(server_name="0.0.0.0")
except Exception as e:
    raise e
finally:
    db_dir = os.path.join(os.path.dirname(__file__), "db")
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)
