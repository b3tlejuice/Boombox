import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, QMenu, QStackedWidget, QLabel
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import Qt

from .widgets.sidebar import Sidebar
from .widgets.player_controls import PlayerControls
from .widgets.media_list import MediaList
from ..core.media_player import MediaPlayer
from ..database.db_manager import db_manager
from ..database.models import Media

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaFlow")
        self.resize(1200, 800)

        # Load Styles
        self.load_styles()

        # Database
        # In a real app we might want to run this in a thread or check connection first
        db_manager.init_db()
        self.session = db_manager.get_session()

        # Core Player
        self.player = MediaPlayer()

        # UI Setup
        self.setup_ui()
        self.connect_signals()

        # Initial Load
        self.refresh_library()

    def load_styles(self):
        style_path = os.path.join("assets", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Upper Area (Sidebar + Content)
        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(0)

        self.sidebar = Sidebar()

        # Content Stack (List, Video, Photo)
        self.content_stack = QStackedWidget()

        # 1. Media List View
        self.media_list = MediaList()
        self.content_stack.addWidget(self.media_list)

        # 2. Video View
        self.video_container = QWidget()
        self.video_container.setStyleSheet("background-color: black;")
        video_layout = QVBoxLayout(self.video_container)
        self.video_widget = QVideoWidget()
        video_layout.addWidget(self.video_widget)

        # Close Video Button (to go back to list)
        self.close_video_btn = self.create_close_button(self.return_to_list)
        video_layout.addWidget(self.close_video_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.content_stack.addWidget(self.video_container)

        # Connect player to video widget
        self.player.set_video_output(self.video_widget)

        # 3. Photo View
        self.photo_container = QWidget()
        self.photo_container.setStyleSheet("background-color: black;")
        photo_layout = QVBoxLayout(self.photo_container)
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_layout.addWidget(self.photo_label)

        self.close_photo_btn = self.create_close_button(self.return_to_list)
        photo_layout.addWidget(self.close_photo_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.content_stack.addWidget(self.photo_container)

        upper_layout.addWidget(self.sidebar)
        upper_layout.addWidget(self.content_stack, 1) # 1 stretch factor

        main_layout.addLayout(upper_layout, 1)

        # Lower Area (Player Controls)
        self.controls = PlayerControls()
        main_layout.addWidget(self.controls)

        # Menu Bar
        self.create_menus()

    def create_close_button(self, callback):
        from PyQt6.QtWidgets import QPushButton
        btn = QPushButton("Close")
        btn.setStyleSheet("background-color: rgba(255, 255, 255, 50); color: white; border: none; padding: 5px 10px; border-radius: 4px;")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def return_to_list(self):
        self.player.stop()
        self.content_stack.setCurrentWidget(self.media_list)
        self.controls.show() # Show controls back if we hid them (optional)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        add_file_action = QAction("Add Media File", self)
        add_file_action.triggered.connect(self.add_media_file)
        file_menu.addAction(add_file_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def connect_signals(self):
        # Sidebar
        self.sidebar.home_btn.clicked.connect(self.return_to_list)
        self.sidebar.library_btn.clicked.connect(self.refresh_library)

        # Media List
        self.media_list.media_selected.connect(self.play_media)

        # Player Controls -> Player
        self.controls.play_clicked.connect(self.player.play)
        self.controls.pause_clicked.connect(self.player.pause)
        self.controls.volume_changed.connect(self.player.set_volume)
        self.controls.seek_position.connect(self.player.set_position)

        # Player -> Player Controls
        self.player.position_changed.connect(self.controls.update_progress)
        self.player.duration_changed.connect(self.controls.update_duration)
        self.player.state_changed.connect(self.on_player_state_changed)

    def add_media_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Media", "", "Media Files (*.mp3 *.wav *.mp4 *.avi *.jpg *.png)")
        if file_path:
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]

            # Simple metadata extraction could go here
            media_type = 'audio' # Default
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                media_type = 'video'
            elif file_path.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp')):
                 media_type = 'photo'

            # Save to DB
            try:
                new_media = Media(title=title, file_path=file_path, media_type=media_type)
                self.session.add(new_media)
                self.session.commit()
                self.refresh_library()
            except Exception as e:
                self.session.rollback()
                print(f"Error adding media: {e}")
                QMessageBox.warning(self, "Error", "Could not add media. It might already exist.")

    def refresh_library(self):
        self.media_list.header_label.setText("Library")
        self.media_list.clear()
        self.content_stack.setCurrentWidget(self.media_list)

        try:
            media_items = self.session.query(Media).all()
            for item in media_items:
                self.media_list.add_media_item(item.title, item.artist, item.file_path)
        except Exception as e:
            print(f"Database error: {e}")

    def play_media(self, file_path):
        # Update UI info
        filename = os.path.basename(file_path)

        # Determine Type
        media_type = 'audio'
        if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            media_type = 'video'
        elif file_path.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp')):
             media_type = 'photo'

        self.controls.update_track_info(filename, "Unknown Artist")

        if media_type == 'photo':
            # Handle Photo
            self.player.stop()
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                 self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                 self.content_stack.setCurrentWidget(self.photo_container)
            else:
                 QMessageBox.warning(self, "Error", "Could not load image.")

        elif media_type == 'video':
            # Handle Video
            self.content_stack.setCurrentWidget(self.video_container)
            self.player.load_media(file_path)
            self.player.play()
            self.controls.set_playing_state(True)

        else:
            # Handle Audio
            # Stay on list view or maybe go to a "Now Playing" view? keeping list view for now like spotify
            self.player.load_media(file_path)
            self.player.play()
            self.controls.set_playing_state(True)

    def on_player_state_changed(self, state):
        from PyQt6.QtMultimedia import QMediaPlayer
        self.controls.set_playing_state(state == QMediaPlayer.PlaybackState.PlayingState)
