from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal

class Sidebar(QWidget):
    playlist_clicked = pyqtSignal(int)
    playlist_delete_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        title_label = QLabel("Boombox")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding-left: 15px; margin-bottom: 20px;")
        layout.addWidget(title_label)

        self.library_btn = self.create_button("Your Library")

        layout.addWidget(self.library_btn)

        playlist_label = QLabel("PLAYLISTS")
        playlist_label.setStyleSheet("color: #B3B3B3; font-size: 12px; font-weight: bold; padding-left: 15px; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(playlist_label)

        self.playlist_list = QListWidget()
        self.playlist_list.setObjectName("playlist_list")
        self.playlist_list.setFrameShape(QListWidget.Shape.NoFrame)
        self.playlist_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playlist_list.itemClicked.connect(self.on_playlist_clicked)

        self.playlist_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.playlist_list.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.playlist_list)

    def create_button(self, text):
        btn = QPushButton(text)
        btn.setProperty("class", "sidebar-btn")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def add_playlist(self, name, playlist_id):
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, playlist_id)
        self.playlist_list.addItem(item)

    def clear_playlists(self):
        self.playlist_list.clear()

    def on_playlist_clicked(self, item):
        playlist_id = item.data(Qt.ItemDataRole.UserRole)
        self.playlist_clicked.emit(playlist_id)

    def show_context_menu(self, position):
        item = self.playlist_list.itemAt(position)
        if not item:
            return

        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        delete_action = menu.addAction("Delete Playlist")

        action = menu.exec(self.playlist_list.mapToGlobal(position))

        if action == delete_action:
            playlist_id = item.data(Qt.ItemDataRole.UserRole)
            self.playlist_delete_requested.emit(playlist_id)
