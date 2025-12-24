from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt6.QtCore import Qt, pyqtSignal

class PlayerControls(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    volume_changed = pyqtSignal(int)
    seek_position = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("player_controls")
        self.setup_ui()
        self.is_playing = False

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 10, 20, 10)
        self.setLayout(main_layout)

        # 1. Left: Track Info
        info_layout = QVBoxLayout()
        self.track_title = QLabel("No Song Playing")
        self.track_title.setObjectName("song_title")
        self.track_artist = QLabel("")
        self.track_artist.setObjectName("artist_name")
        info_layout.addWidget(self.track_title)
        info_layout.addWidget(self.track_artist)

        main_layout.addLayout(info_layout, 1)

        # 2. Center: Controls
        controls_container = QVBoxLayout()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setProperty("class", "control-btn")
        self.prev_btn.clicked.connect(self.prev_clicked)

        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("play_btn")
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.clicked.connect(self.toggle_play)

        self.next_btn = QPushButton("⏭")
        self.next_btn.setProperty("class", "control-btn")
        self.next_btn.clicked.connect(self.next_clicked)

        buttons_layout.addWidget(self.prev_btn)
        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.next_btn)

        # Progress Bar
        progress_layout = QHBoxLayout()
        self.current_time_lbl = QLabel("0:00")
        self.total_time_lbl = QLabel("0:00")

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.seek_position)

        progress_layout.addWidget(self.current_time_lbl)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.total_time_lbl)

        controls_container.addLayout(buttons_layout)
        controls_container.addLayout(progress_layout)

        main_layout.addLayout(controls_container, 2)

        # 3. Right: Volume
        volume_layout = QHBoxLayout()
        volume_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        vol_icon = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.volume_changed)

        volume_layout.addWidget(vol_icon)
        volume_layout.addWidget(self.volume_slider)

        main_layout.addLayout(volume_layout, 1)

    def toggle_play(self):
        if self.is_playing:
            self.play_btn.setText("▶")
            self.pause_clicked.emit()
            self.is_playing = False
        else:
            self.play_btn.setText("⏸")
            self.play_clicked.emit()
            self.is_playing = True

    def set_playing_state(self, playing):
        self.is_playing = playing
        self.play_btn.setText("⏸" if playing else "▶")

    def update_track_info(self, title, artist):
        self.track_title.setText(title)
        self.track_artist.setText(artist)

    def update_progress(self, position):
        self.progress_slider.setValue(position)
        self.current_time_lbl.setText(self.format_time(position))

    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)
        self.total_time_lbl.setText(self.format_time(duration))

    def format_time(self, ms):
        seconds = (ms // 1000) % 60
        minutes = (ms // 60000)
        return f"{minutes}:{seconds:02}"
