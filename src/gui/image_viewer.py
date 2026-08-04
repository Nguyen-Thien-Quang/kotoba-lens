from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Supported image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}


class ImageViewerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("kotoba lens~")
        self.resize(1000, 600)

        # --- Layouts ---
        main_layout = QVBoxLayout(self)

        # Top Bar: Upload Button & Selected Folder Path Label
        top_bar_layout = QHBoxLayout()
        self.btn_upload = QPushButton("📁 Select Folder")
        self.btn_upload.setFixedHeight(40)
        self.lbl_folder_path = QLabel("No folder selected")
        self.lbl_folder_path.setStyleSheet("color: #665; font-style: italic;")

        top_bar_layout.addWidget(self.btn_upload)
        top_bar_layout.addWidget(self.lbl_folder_path)
        top_bar_layout.addStretch()

        # Content Area: Split between Thumbnail List and Image Display
        content_layout = QHBoxLayout()

        # Left side: List of images
        self.image_list = QListWidget()
        self.image_list.setFixedWidth(250)
        self.image_list.setIconSize(QSize(60, 60))

        # Right side: Main Image Preview
        self.image_preview = QLabel("Select an image from the list to view")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet(
            "border: 2px dashed #cccccc; background-color: #f9f9f9;"
        )
        
        self.image_preview.setMinimumSize(1, 1)

        content_layout.addWidget(self.image_list)
        content_layout.addWidget(self.image_preview, stretch=1)

        # Add top bar and content area to main layout
        main_layout.addLayout(top_bar_layout)
        main_layout.addLayout(content_layout)

        # --- Signal Connections ---
        self.btn_upload.clicked.connect(self.open_folder_dialog)
        self.image_list.itemClicked.connect(self.display_image)

        # Keep track of current image pixmap for proper resizing
        self.current_pixmap = None

    def open_folder_dialog(self):
        """Opens a file dialog to select a directory."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            caption="Select Folder containing Images",
            dir="",
            options=QFileDialog.Option.ShowDirsOnly,
        )

        if folder_path:
            self.lbl_folder_path.setText(folder_path)
            self.load_images_from_folder(folder_path)

    def load_images_from_folder(self, folder_path):
        """Scans the selected folder and populates the sidebar list."""
        self.image_list.clear()
        folder = Path(folder_path)

        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
                item = QListWidgetItem(file_path.name)
                # Store full Path object in custom user role
                item.setData(Qt.ItemDataRole.UserRole, file_path)

                # Set a small thumbnail icon in the list
                pixmap = QPixmap(str(file_path))
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio)))

                self.image_list.addItem(item)

    def display_image(self, item):
        """Displays the clicked image in the main preview area."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.current_pixmap = QPixmap(str(file_path))
        self.update_preview()

    def update_preview(self):
        """Scales and updates the preview image when loaded or resized."""

        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_preview.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Ensure the preview image resizes smoothly when window resizes."""
        super().resizeEvent(event)
        self.update_preview()


