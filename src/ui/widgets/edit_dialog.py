from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class MediaEditDialog(QDialog):
    def __init__(self, media_item, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Media Info")
        self.resize(400, 500)
        self.media_item = media_item
        self.custom_cover_path = media_item.custom_cover_path
        self.deleted = False

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)

        layout.addWidget(QLabel("Artist:"))
        self.artist_edit = QLineEdit()
        layout.addWidget(self.artist_edit)

        layout.addWidget(QLabel("Cover Art:"))
        self.cover_lbl = QLabel()
        self.cover_lbl.setFixedSize(200, 200)
        self.cover_lbl.setStyleSheet("background-color: #333; border: 1px solid #555;")
        self.cover_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cover_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        self.browse_cover_btn = QPushButton("Browse...")
        self.browse_cover_btn.clicked.connect(self.browse_cover)
        self.clear_cover_btn = QPushButton("Clear Custom Cover")
        self.clear_cover_btn.clicked.connect(self.clear_cover)

        btn_layout.addWidget(self.browse_cover_btn)
        btn_layout.addWidget(self.clear_cover_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

        actions_layout = QHBoxLayout()

        self.delete_btn = QPushButton("Delete Media")
        self.delete_btn.setStyleSheet("background-color: #aa2222; color: white; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_media)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        actions_layout.addWidget(self.delete_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.cancel_btn)

        layout.addLayout(actions_layout)

    def load_data(self):
        self.title_edit.setText(self.media_item.title or "")
        self.artist_edit.setText(self.media_item.artist or "")

        self.update_cover_display()

    def update_cover_display(self):
        if self.custom_cover_path and os.path.exists(self.custom_cover_path):
             pixmap = QPixmap(self.custom_cover_path)
             if not pixmap.isNull():
                 self.cover_lbl.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                 return

        self.cover_lbl.setText("No Custom Cover")

    def browse_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cover Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.custom_cover_path = file_path
            self.update_cover_display()

    def clear_cover(self):
        self.custom_cover_path = None
        self.update_cover_display()

    def delete_media(self):
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this media from the library?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.deleted = True
            self.accept()

    def get_data(self):
        return {
            'title': self.title_edit.text(),
            'artist': self.artist_edit.text(),
            'custom_cover_path': self.custom_cover_path
        }
