import os
import shutil
from gradio_ui.ui import create_ui

try:
    demo = create_ui()
    demo.launch()
except Exception as e:
    print("Error launching the app:", e)
finally:
    db_dir = os.path.join(os.path.dirname(__file__), "db")
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)