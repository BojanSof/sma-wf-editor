from io import BytesIO

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QByteArray, QBuffer


class PreviewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gif = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Watch Face Preview")

        self.gif_view = QLabel()
        self.gif_view.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)

        layout = QVBoxLayout()
        layout.addWidget(self.gif_view)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def set_gif(self, imgs):
        self.gif_data = BytesIO()
        imgs[0].save(fp=self.gif_data, format="GIF", save_all=True, append_images=imgs[1:], delay=200, loop=0)

        self.data_bytes = QByteArray(self.gif_data.getvalue())
        self.data_buffer = QBuffer(self.data_bytes)

        if self.gif is not None:
            self.gif.stop()

        self.gif = QMovie(self.data_buffer)
        self.gif.setCacheMode(QMovie.CacheMode.CacheAll)
        self.gif_view.setMovie(self.gif)
        self.gif.start()


    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "GIF Files (*.gif)")
        if file_name:
            with open(file_name, "wb") as f:
                f.write(self.gif_data.getvalue())
            QMessageBox.information(self, "Save Image", "Image saved successfully")
