import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, QMenu, QStackedWidget, QLabel
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import Qt

from .widgets.sidebar import Sidebar
from .widgets.player_controls import PlayerControls
from PyQt6.QtWidgets import QInputDialog
from .widgets.media_list import MediaList
from .widgets.edit_dialog import MediaEditDialog
from ..core.media_player import MediaPlayer
from ..core.metadata import extract_metadata
from ..database.db_manager import db_manager
from ..database.models import Media, Playlist

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Boombox")
        self.resize(1200, 800)

        self.load_styles()

        db_manager.init_db()
        self.session = db_manager.get_session()

        self.player = MediaPlayer()

        self.setup_ui()
        self.connect_signals()

        self.current_playlist_id = None
        self.current_sort_mode = "date_desc"
        self.current_media_type = None

        self.refresh_library()
        self.load_playlists_sidebar()

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

        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(0)

        self.sidebar = Sidebar()

        self.content_stack = QStackedWidget()

        self.media_list = MediaList()
        self.content_stack.addWidget(self.media_list)

        self.video_container = QWidget()
        self.video_container.setStyleSheet("background-color: black;")
        video_layout = QVBoxLayout(self.video_container)
        self.video_widget = QVideoWidget()
        video_layout.addWidget(self.video_widget)

        self.close_video_btn = self.create_close_button(self.return_to_list)
        video_layout.addWidget(self.close_video_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.content_stack.addWidget(self.video_container)

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
        upper_layout.addWidget(self.content_stack, 1)

        main_layout.addLayout(upper_layout, 1)

        self.controls = PlayerControls()
        main_layout.addWidget(self.controls)

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
        self.controls.show()

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        add_file_action = QAction("Add Media File", self)
        add_file_action.triggered.connect(self.add_media_file)
        file_menu.addAction(add_file_action)

        create_playlist_action = QAction("Create Playlist", self)
        create_playlist_action.triggered.connect(self.create_playlist)
        file_menu.addAction(create_playlist_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        sort_menu = menubar.addMenu("Sort")

        sort_date_desc = QAction("Date Added (Newest)", self)
        sort_date_desc.triggered.connect(lambda: self.change_sort("date_desc"))
        sort_menu.addAction(sort_date_desc)

        sort_date_asc = QAction("Date Added (Oldest)", self)
        sort_date_asc.triggered.connect(lambda: self.change_sort("date_asc"))
        sort_menu.addAction(sort_date_asc)

        sort_title = QAction("Title (A-Z)", self)
        sort_title.triggered.connect(lambda: self.change_sort("title_asc"))
        sort_menu.addAction(sort_title)

        sort_artist = QAction("Artist (A-Z)", self)
        sort_artist.triggered.connect(lambda: self.change_sort("artist_asc"))
        sort_menu.addAction(sort_artist)

    def connect_signals(self):
        self.sidebar.library_btn.clicked.connect(self.refresh_library)
        self.sidebar.playlist_clicked.connect(self.show_playlist)
        self.sidebar.playlist_delete_requested.connect(self.delete_playlist)

        self.media_list.media_selected.connect(self.play_media)
        self.media_list.context_menu_requested.connect(self.on_media_context_menu)

        self.controls.title_clicked.connect(self.return_to_media_view)

        self.controls.play_clicked.connect(self.player.play)
        self.controls.pause_clicked.connect(self.player.pause)
        self.controls.volume_changed.connect(self.player.set_volume)
        self.controls.seek_position.connect(self.player.set_position)

        self.player.position_changed.connect(self.controls.update_progress)
        self.player.duration_changed.connect(self.controls.update_duration)
        self.player.state_changed.connect(self.on_player_state_changed)

    def add_media_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Media", "", "Media Files (*.mp3 *.wav *.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.jpg *.png *.gif)")
        if file_path:
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]

            media_type = 'audio'
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v')):
                media_type = 'video'
            elif file_path.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp', '.gif')):
                 media_type = 'photo'

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
        self.current_playlist_id = None
        self.media_list.header_label.setText("Library")
        self.media_list.clear()
        self.content_stack.setCurrentWidget(self.media_list)

        try:
            query = self.session.query(Media)

            if self.current_sort_mode == "date_desc":
                query = query.order_by(Media.date_added.desc())
            elif self.current_sort_mode == "date_asc":
                query = query.order_by(Media.date_added.asc())
            elif self.current_sort_mode == "title_asc":
                query = query.order_by(Media.title.asc())
            elif self.current_sort_mode == "artist_asc":
                query = query.order_by(Media.artist.asc())

            media_items = query.all()
            for item in media_items:
                self.media_list.add_media_item(item.title, item.artist, item.file_path, item.id, item.date_added)
        except Exception as e:
            print(f"Database error: {e}")

    def change_sort(self, sort_mode):
        self.current_sort_mode = sort_mode
        if self.current_playlist_id is None:
            self.refresh_library()

    def create_playlist(self):
        name, ok = QInputDialog.getText(self, "Create Playlist", "Playlist Name:")
        if ok and name:
            try:
                new_playlist = Playlist(name=name)
                self.session.add(new_playlist)
                self.session.commit()
                QMessageBox.information(self, "Success", f"Playlist '{name}' created!")
                self.load_playlists_sidebar()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Could not create playlist: {e}")

    def load_playlists_sidebar(self):
        self.sidebar.clear_playlists()
        try:
            playlists = self.session.query(Playlist).all()
            for pl in playlists:
                self.sidebar.add_playlist(pl.name, pl.id)
        except Exception as e:
            print(f"Error loading playlists: {e}")

    def show_playlist(self, playlist_id):
        self.current_playlist_id = playlist_id
        playlist = self.session.query(Playlist).get(playlist_id)
        if not playlist:
            return

        self.media_list.header_label.setText(playlist.name)
        self.media_list.clear()
        self.content_stack.setCurrentWidget(self.media_list)

        for item in playlist.media_items:
             self.media_list.add_media_item(item.title, item.artist, item.file_path, item.id)

    def delete_playlist(self, playlist_id):
        playlist = self.session.query(Playlist).get(playlist_id)
        if not playlist:
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete playlist '{playlist.name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.session.delete(playlist)
                self.session.commit()
                self.load_playlists_sidebar()
                if self.current_playlist_id == playlist_id:
                    self.refresh_library()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Could not delete playlist: {e}")

    def on_media_context_menu(self, position):
        item = self.media_list.list_widget.itemAt(position)
        if not item:
            return

        media_id = item.data(Qt.ItemDataRole.UserRole + 1)

        menu = QMenu()

        if self.current_playlist_id is None:
             playlists = self.session.query(Playlist).all()
             if playlists:
                 add_menu = menu.addMenu("Add to Playlist")
                 for pl in playlists:
                     action = add_menu.addAction(pl.name)
                     action.triggered.connect(lambda checked, pid=pl.id, mid=media_id: self.add_to_playlist(mid, pid))

        if self.current_playlist_id is not None:
            remove_action = menu.addAction("Remove from Playlist")
            remove_action.triggered.connect(lambda: self.remove_from_playlist(media_id, self.current_playlist_id))

        menu.addSeparator()
        edit_action = menu.addAction("Edit Info")
        delete_action = menu.addAction("Delete from Library")

        action = menu.exec(self.media_list.list_widget.mapToGlobal(position))

        if action == edit_action:
            self.open_edit_dialog(media_id)
        elif action == delete_action:
            self.delete_media(media_id)

    def add_to_playlist(self, media_id, playlist_id):
        try:
            playlist = self.session.query(Playlist).get(playlist_id)
            media = self.session.query(Media).get(media_id)
            if playlist and media:
                if media not in playlist.media_items:
                    playlist.media_items.append(media)
                    self.session.commit()
                    QMessageBox.information(self, "Success", f"Added to {playlist.name}")
                else:
                    QMessageBox.warning(self, "Info", "Already in playlist.")
        except Exception as e:
            self.session.rollback()
            print(f"Error adding to playlist: {e}")

    def remove_from_playlist(self, media_id, playlist_id):
        try:
            playlist = self.session.query(Playlist).get(playlist_id)
            media = self.session.query(Media).get(media_id)
            if playlist and media:
                if media in playlist.media_items:
                    playlist.media_items.remove(media)
                    self.session.commit()
                    self.show_playlist(playlist_id)
        except Exception as e:
            self.session.rollback()
            print(f"Error removing from playlist: {e}")

    def open_edit_dialog(self, media_id):
        media_item = self.session.query(Media).get(media_id)
        if not media_item:
            return

        dialog = MediaEditDialog(media_item, self)
        if dialog.exec():
            if dialog.deleted:
                self.delete_media(media_id, confirm=False)
                return

            data = dialog.get_data()
            media_item.title = data['title']
            media_item.artist = data['artist']
            media_item.custom_cover_path = data['custom_cover_path']

            try:
                self.session.commit()
                self.refresh_library()

            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Could not save changes: {e}")

    def delete_media(self, media_id, confirm=True):
        media_item = self.session.query(Media).get(media_id)
        if not media_item:
            return

        if confirm:
            reply = QMessageBox.question(self, "Confirm Delete",
                                         f"Are you sure you want to delete '{media_item.title}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            self.session.delete(media_item)
            self.session.commit()
            self.refresh_library()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Error", f"Could not delete media: {e}")

    def play_media(self, file_path):
        media_type = 'audio'
        if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v')):
            media_type = 'video'
        elif file_path.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp', '.gif')):
             media_type = 'photo'

        if media_type == 'video':
            self.player.set_video_output(self.video_widget)
        else:
            self.player.set_video_output(None)

        self.current_media_type = media_type

        db_media = self.session.query(Media).filter_by(file_path=file_path).first()

        metadata = extract_metadata(file_path)

        title = metadata.get('title', "Unknown Title")
        artist = metadata.get('artist', "Unknown Artist")
        cover_image = metadata.get('cover_art')
        cover_pixmap = QPixmap.fromImage(cover_image) if cover_image else None

        if db_media:
            if db_media.title:
                title = db_media.title
            if db_media.artist:
                artist = db_media.artist

            if db_media.custom_cover_path and os.path.exists(db_media.custom_cover_path):
                custom_pixmap = QPixmap(db_media.custom_cover_path)
                if not custom_pixmap.isNull():
                    cover_pixmap = custom_pixmap

        if media_type in ['video', 'photo']:
            self.controls.update_track_info(title, "", cover_pixmap)
        else:
            self.controls.update_track_info(title, artist, cover_pixmap)

        if media_type == 'photo':
            self.player.stop()
            if file_path.lower().endswith('.gif'):
                from PyQt6.QtGui import QMovie
                movie = QMovie(file_path)
                self.photo_label.setMovie(movie)
                movie.start()
                self.content_stack.setCurrentWidget(self.photo_container)
            else:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                     self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                     self.content_stack.setCurrentWidget(self.photo_container)
                else:
                     QMessageBox.warning(self, "Error", "Could not load image.")

        elif media_type == 'video':
            self.content_stack.setCurrentWidget(self.video_container)
            self.player.load_media(file_path)
            self.player.play()
            self.controls.set_playing_state(True)

        else:
            self.content_stack.setCurrentWidget(self.media_list)
            self.player.load_media(file_path)
            self.player.play()
            self.controls.set_playing_state(True)

    def return_to_media_view(self):
        if self.current_media_type == 'video':
            self.content_stack.setCurrentWidget(self.video_container)
        elif self.current_media_type == 'photo':
            self.content_stack.setCurrentWidget(self.photo_container)

    def on_player_state_changed(self, state):
        from PyQt6.QtMultimedia import QMediaPlayer
        self.controls.set_playing_state(state == QMediaPlayer.PlaybackState.PlayingState)
