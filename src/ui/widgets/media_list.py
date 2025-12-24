from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal

class MediaList(QWidget):
    media_selected = pyqtSignal(str) # Emits file path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content_area")
        self.setup_ui()
        self.items_map = {} # Map row to file path

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header
        self.header_label = QLabel("Library")
        self.header_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white; margin-bottom: 20px;")
        layout.addWidget(self.header_label)

        # List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

    def add_media_item(self, title, artist, file_path):
        display_text = f"{title} - {artist}" if artist else title
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)

    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.media_selected.emit(file_path)

    def clear(self):
        self.list_widget.clear()
