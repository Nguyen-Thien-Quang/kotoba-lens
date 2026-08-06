import sys
from gui.image_viewer import ImageViewerApp
from PySide6.QtWidgets import QApplication
from app_context import AppContext

if __name__ == "__main__":
    app = QApplication(sys.argv)

    context = AppContext()
    conn = context.connection
    rules = context.deinflection_rules
    model = context.model

    window = ImageViewerApp(context)
    window.show()
    sys.exit(app.exec())
