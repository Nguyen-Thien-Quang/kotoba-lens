import sys
from gui.image_viewer import ImageViewerApp
from PySide6.QtWidgets import QApplication
from app_context import AppContext

if __name__ == "__main__":
    context = AppContext()
    conn = context.connection
    rules = context.deinflection_rules
    model = context.model

    app = QApplication(sys.argv)

    window = ImageViewerApp(context)
    window.show()
    try:
        sys.exit(app.exec())
    finally:
        context.connection.commit()
        context.connection.close()

