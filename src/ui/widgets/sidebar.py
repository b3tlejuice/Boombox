from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        # Logo / Title
        title_label = QLabel("MediaFlow")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding-left: 15px; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Navigation Buttons
        self.home_btn = self.create_button("Home")
        self.library_btn = self.create_button("Your Library")
        self.create_playlist_btn = self.create_button("Create Playlist")

        layout.addWidget(self.home_btn)
        layout.addWidget(self.library_btn)
        layout.addWidget(self.create_playlist_btn)

        # Spacer to push everything up
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Maybe a list of playlists here later

    def create_button(self, text):
        btn = QPushButton(text)
        btn.setProperty("class", "sidebar-btn")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
