import numpy as np
from scipy import signal
from PyQt6.QtCore import QObject, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtMultimedia import QAudioSink, QMediaDevices, QAudioFormat, QAudioBuffer

class EqualizerProcessor(QObject):
    visualizer_data_ready = pyqtSignal(np.ndarray, int, int)

    def __init__(self):
        super().__init__()
        self.sink = None
        self.device = None
        self.current_format = None
        self.gains = [0.0] * 10
        self.frequencies = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        self.filter_sos = [None] * 10
        self.filter_zi = [None] * 10
        self.enabled = False
        self.current_volume = 0.7

        self.recalculate_filters(44100)

    def recalculate_filters(self, fs):
        pass

    def _design_peaking_equalizer(self, center_freq, gain_db, Q, fs):
        A = 10 ** (gain_db / 40.0)
        w0 = 2 * np.pi * center_freq / fs
        alpha = np.sin(w0) / (2 * Q)

        cos_w0 = np.cos(w0)

        b0 = 1 + alpha * A
        b1 = -2 * cos_w0
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * cos_w0
        a2 = 1 - alpha / A

        return np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])

    @pyqtSlot(list)
    def update_gains(self, new_gains_db):
        self.gains = new_gains_db
        if self.current_format:
            self.update_filters(self.current_format.sampleRate())

    @pyqtSlot(int)
    def set_volume(self, volume):
        self.current_volume = volume / 100.0
        if self.sink:
            self.sink.setVolume(self.current_volume)

    def update_filters(self, fs):
        for i, freq in enumerate(self.frequencies):
            sos = self._design_peaking_equalizer(freq, self.gains[i], 1.414, fs)
            self.filter_sos[i] = sos

            if self.filter_zi[i] is None:
                 self.filter_zi[i] = np.zeros((1, 2))

    @pyqtSlot(QAudioBuffer)
    def process_buffer(self, buffer):
        if not self.enabled:
            return

        format = buffer.format()
        if not format.isValid():
            return

        if self.sink is None or self.current_format != format:
            self.current_format = format
            self.update_filters(format.sampleRate())

            device_info = QMediaDevices.defaultAudioOutput()
            self.sink = QAudioSink(device_info, format)
            self.sink.setVolume(self.current_volume)
            self.device = self.sink.start()

            self.filter_zi = [np.zeros((1, 2)) for _ in range(10)]

        data_bytes = buffer.data()

        try:
            if format.sampleFormat() == QAudioFormat.SampleFormat.Int16:
                audio_data = np.frombuffer(data_bytes, dtype=np.int16).astype(np.float32)
                scaler = 32768.0
            elif format.sampleFormat() == QAudioFormat.SampleFormat.Float:
                audio_data = np.frombuffer(data_bytes, dtype=np.float32)
                scaler = 1.0
            else:
                return

            processed_data = audio_data / scaler

            channels = format.channelCount()
            if channels > 1:
                processed_data = processed_data.reshape(-1, channels)

            for i in range(10):
                if abs(self.gains[i]) > 0.1:
                    if channels > 1:
                        target_shape = (1, channels, 2)
                        if self.filter_zi[i].shape != target_shape:
                             self.filter_zi[i] = np.zeros(target_shape)

                        processed_data, self.filter_zi[i] = signal.sosfilt(
                            self.filter_sos[i],
                            processed_data,
                            axis=0,
                            zi=self.filter_zi[i]
                        )
                    else:
                        if self.filter_zi[i].ndim == 3:
                            self.filter_zi[i] = np.zeros((1, 2))

                        processed_data, self.filter_zi[i] = signal.sosfilt(
                            self.filter_sos[i],
                            processed_data,
                            axis=0,
                            zi=self.filter_zi[i]
                        )

            vis_data = processed_data
            if channels > 1:
                vis_data = np.mean(vis_data, axis=1)

            window = np.hanning(len(vis_data))
            fft_mag = np.abs(np.fft.rfft(vis_data * window))

            fft_mag = fft_mag / len(vis_data) * 200

            self.visualizer_data_ready.emit(fft_mag, format.sampleRate(), len(vis_data))

            processed_data = processed_data * scaler
            processed_data = np.clip(processed_data, -scaler, scaler-1)

            if format.sampleFormat() == QAudioFormat.SampleFormat.Int16:
                out_bytes = processed_data.astype(np.int16).tobytes()
            elif format.sampleFormat() == QAudioFormat.SampleFormat.Float:
                out_bytes = processed_data.astype(np.float32).tobytes()
            else:
                out_bytes = data_bytes

            if self.device:
                self.device.write(out_bytes)

        except Exception as e:
            pass

    def start(self):
        self.enabled = True

    def stop(self):
        self.enabled = False
        if self.sink:
            self.sink.stop()
            self.sink = None
            self.device = None
