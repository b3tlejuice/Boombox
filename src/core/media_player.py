from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, pyqtSignal, QObject

class MediaPlayer(QObject):
    # Signals to update UI
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    media_status_changed = pyqtSignal(QMediaPlayer.MediaStatus)
    state_changed = pyqtSignal(QMediaPlayer.PlaybackState)

    def __init__(self):
        super().__init__()
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

        # Connect internal signals
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.mediaStatusChanged.connect(self.media_status_changed)
        self._player.playbackStateChanged.connect(self.state_changed)

        self._current_volume = 70

    def _on_position_changed(self, position):
        self.position_changed.emit(position)

    def _on_duration_changed(self, duration):
        self.duration_changed.emit(duration)
        self._audio_output.setVolume(self._current_volume / 100)

    def set_video_output(self, video_widget):
        """Sets the widget where video will be rendered."""
        self._player.setVideoOutput(video_widget)

    def load_media(self, file_path):
        """Loads media from a local file path."""
        url = QUrl.fromLocalFile(file_path)
        self._player.setSource(url)

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def stop(self):
        self._player.stop()

    def set_position(self, position):
        self._player.setPosition(position)

    def set_volume(self, volume):
        """Volume 0-100"""
        self._current_volume = volume
        self._audio_output.setVolume(volume / 100)

    def get_state(self):
        return self._player.playbackState()

    def is_playing(self):
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
