import os
import shutil

from gradio_ui.ui import create_ui
from views import GradioView






try:
    gradio_view = GradioView()
    gradio_view.launch("0.0.0.0")
except Exception as e:
    raise e
finally:
    db_dir = os.path.join(os.path.dirname(__file__), "db")
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)
