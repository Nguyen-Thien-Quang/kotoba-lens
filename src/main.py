from os import close
import sys
from gui.image_viewer import ImageViewerApp
from PySide6.QtWidgets import QApplication
from app_context import AppContext

if __name__ == "__main__":
    context = AppContext()
    conn = context.connection

    app = QApplication(sys.argv)

    window = ImageViewerApp(context)
    window.show()
    try:
        sys.exit(app.exec())
    finally:
        # close main database
        conn.commit()
        conn.close()
        # close dictionary database
        context.dict_DB_connection.commit()
        context.dict_DB_connection.close()
