import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QSlider,
                             QLabel, QStyle, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon
import vlc


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Agudie Media Player")
        self.setGeometry(100, 100, 800, 600)

        # Create VLC instance and media player
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create layouts
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Video display
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.video_frame)

        # Control bar
        self.control_layout = QHBoxLayout()
        self.main_layout.addLayout(self.control_layout)

        # Create buttons
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)

        self.open_button = QPushButton("Open Video")
        self.open_button.clicked.connect(self.open_file)

        # Volume control
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)

        # Time label
        self.time_label = QLabel("00:00:00 / 00:00:00")

        # Add widgets to control layout
        self.control_layout.addWidget(self.open_button)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.stop_button)
        self.control_layout.addWidget(self.volume_slider)
        self.control_layout.addWidget(self.time_label)

        # Add position slider to main layout
        self.main_layout.addWidget(self.position_slider)

        # Timer to update the position slider
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui)

        # Set video output to the video_frame
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.media_player.set_nsobject(self.video_frame.winId())

        # Set initial volume
        self.media_player.audio_set_volume(50)

    def open_file(self):
        """Open a media file in a FileDialog."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File",
                                                   os.path.expanduser('~'),
                                                   "Media Files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv);;All Files (*)")

        if file_path:
            # Create the media
            media = self.instance.media_new(file_path)
            self.media_player.set_media(media)

            # Parse the metadata of the file
            media.parse()

            # Set the title of the track as window title
            self.setWindowTitle(f"Python Media Player - {os.path.basename(file_path)}")

            # Start playing the video
            self.play_pause()

    def play_pause(self):
        """Toggle play/pause status."""
        if not self.media_player.get_media():
            self.open_file()
            return

        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.timer.start()

    def stop(self):
        """Stop the player."""
        self.media_player.stop()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.timer.stop()
        self.time_label.setText("00:00:00 / 00:00:00")
        self.position_slider.setValue(0)

    def set_volume(self, volume):
        """Set the volume."""
        self.media_player.audio_set_volume(volume)

    def set_position(self, position):
        """Set the position of the video."""
        # Set the media position (0.0 to 1.0)
        self.media_player.set_position(position / 1000.0)

    def update_ui(self):
        """Update the position slider and time label."""
        if not self.media_player.get_media():
            return

        # Update position slider
        media_pos = int(self.media_player.get_position() * 1000)
        self.position_slider.setValue(media_pos)

        # Update time label
        current_time = self.media_player.get_time() // 1000  # in seconds
        total_time = self.media_player.get_length() // 1000  # in seconds

        if total_time > 0:
            current_time_str = self.format_time(current_time)
            total_time_str = self.format_time(total_time)
            self.time_label.setText(f"{current_time_str} / {total_time_str}")

        # If media is not playing, stop timer
        if not self.media_player.is_playing():
            self.timer.stop()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def format_time(self, seconds):
        """Format seconds into HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def closeEvent(self, event):
        """Clean up on close."""
        self.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())