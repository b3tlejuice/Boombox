from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from datetime import datetime

class MediaList(QWidget):
    media_selected = pyqtSignal(str)
    context_menu_requested = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content_area")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.header_label = QLabel("Library")
        self.header_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white; margin-bottom: 20px;")
        layout.addWidget(self.header_label)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

    def add_media_item(self, title, artist, file_path, media_id, date_added=None):
        display_text = f"{title}"
        if artist:
            display_text += f" - {artist}"

        if date_added:
            date_str = date_added.strftime("%Y-%m-%d")
            display_text += f"  (Added: {date_str})"

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setData(Qt.ItemDataRole.UserRole + 1, media_id)
        self.list_widget.addItem(item)

    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.media_selected.emit(file_path)

    def show_context_menu(self, position):
        self.context_menu_requested.emit(position)

    def clear(self):
        self.list_widget.clear()
