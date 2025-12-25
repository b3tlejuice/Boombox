import numpy as np
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer, QRectF, QThread
from PyQt6.QtGui import QPainter, QColor, QBrush, QLinearGradient
from PyQt6.QtMultimedia import QAudioBufferOutput, QAudioBuffer

from ...core.equalizer_processor import EqualizerProcessor

class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setStyleSheet("background-color: #111;")
        self.bars = 30
        self.values = [0.0] * self.bars
        self.gains = [1.0] * 10

    def update_data(self, fft_mag, sample_rate, total_samples):
        if len(fft_mag) == 0:
             return

        min_freq = 20
        max_freq = 20000

        log_bins = np.logspace(np.log10(min_freq), np.log10(max_freq), self.bars + 1)

        freq_per_bin = sample_rate / total_samples

        new_values = []
        for i in range(self.bars):
            start_freq = log_bins[i]
            end_freq = log_bins[i+1]

            start_bin = int(start_freq / freq_per_bin)
            end_bin = int(end_freq / freq_per_bin)

            start_bin = max(0, min(start_bin, len(fft_mag) - 1))
            end_bin = max(start_bin + 1, min(end_bin, len(fft_mag)))

            chunk = fft_mag[start_bin:end_bin]

            val = 0.0
            if len(chunk) > 0:
                val = np.mean(chunk)

            new_values.append(min(1.0, val))

        self.values = new_values
        self.update()

    def set_gains(self, gains):
        self.gains = gains

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        bar_width = width / self.bars

        for i, val in enumerate(self.values):
            bar_height = val * height
            x = i * bar_width
            y = height - bar_height

            rect = QRectF(x + 1, y, bar_width - 2, bar_height)

            gradient = QLinearGradient(x, height, x, 0)
            gradient.setColorAt(0, QColor(0, 255, 0))
            gradient.setColorAt(0.5, QColor(255, 255, 0))
            gradient.setColorAt(1, QColor(255, 0, 0))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)

class EqualizerWindow(QMainWindow):
    def __init__(self, player_instance, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Equalizer")
        self.resize(600, 400)
        self.player = player_instance
        self.slider_gains_db = [0.0] * 10

        try:
             self.buffer_output = QAudioBufferOutput()
             self.player.set_audio_buffer_output(self.buffer_output)
        except Exception as e:
            print(f"Could not initialize Audio Buffer Output: {e}")
            self.buffer_output = None

        self.processor_thread = QThread()
        self.processor = EqualizerProcessor()
        self.processor.moveToThread(self.processor_thread)
        self.processor_thread.start()

        if self.buffer_output:
            self.buffer_output.audioBufferReceived.connect(self.processor.process_buffer)

        self.processor.visualizer_data_ready.connect(self.on_visualizer_data)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #222; color: white;")

        layout = QVBoxLayout(central_widget)

        self.visualizer = VisualizerWidget()
        layout.addWidget(self.visualizer)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        sliders_layout = QHBoxLayout()
        layout.addLayout(sliders_layout)

        frequencies = ["32", "64", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]

        for i, freq in enumerate(frequencies):
            band_layout = QVBoxLayout()

            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-12, 12)
            slider.setValue(0)
            slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            slider.setStyleSheet("""
                QSlider::groove:vertical {
                    background: #444;
                    width: 6px;
                    border-radius: 3px;
                }
                QSlider::handle:vertical {
                    background: #00ccff;
                    height: 14px;
                    margin: 0 -4px;
                    border-radius: 7px;
                }
                QSlider::add-page:vertical {
                    background: #00ccff;
                }
                QSlider::sub-page:vertical {
                    background: #444;
                }
            """)

            slider.valueChanged.connect(lambda val, idx=i: self.update_gain(idx, val))

            label = QLabel(freq)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 10px; color: #aaa;")

            band_layout.addWidget(slider, 1, Qt.AlignmentFlag.AlignHCenter)
            band_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignHCenter)

            sliders_layout.addLayout(band_layout)

        preamp_layout = QVBoxLayout()
        preamp_slider = QSlider(Qt.Orientation.Vertical)
        preamp_slider.setRange(0, 100)
        preamp_slider.setValue(70)
        preamp_slider.valueChanged.connect(self.player.set_volume)
        preamp_slider.valueChanged.connect(self.processor.set_volume)

        preamp_label = QLabel("Preamp")
        preamp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preamp_layout.addWidget(preamp_slider, 1, Qt.AlignmentFlag.AlignHCenter)
        preamp_layout.addWidget(preamp_label, 0, Qt.AlignmentFlag.AlignHCenter)

        sliders_layout.addLayout(preamp_layout)

    def update_gain(self, index, value):
        self.slider_gains_db[index] = float(value)
        self.processor.update_gains(self.slider_gains_db)

    def on_visualizer_data(self, fft_mag, sample_rate, total_samples):
        self.visualizer.update_data(fft_mag, sample_rate, total_samples)

    def showEvent(self, event):
        self.player.set_muted(True)
        self.processor.start()
        super().showEvent(event)

    def closeEvent(self, event):
        self.processor.stop()
        self.player.set_muted(False)
        super().closeEvent(event)
