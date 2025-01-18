from PySide6.QtWidgets import (
    QListWidgetItem,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QFileDialog,
)
from PySide6.QtCore import Qt


class WatchFaceLayer(QListWidgetItem):
    def __init__(self, name=None, image=None, parent=None):
        super().__init__(parent)

        self.widget = QWidget()
        self.image_label = QLabel()
        self.image_label.setFixedSize(50, 50)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Enter name")
        if name:
            self.name_field.setText(name)

        self.load_button = QPushButton("...")
        self.load_button.clicked.connect(self.load_image)

        layout = QHBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_field)
        layout.addWidget(self.load_button)

        self.widget.setLayout(layout)
        self.setSizeHint(self.widget.sizeHint())

        if image:
            self.set_image(image)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.widget, "Open Image File", "", "Images (*.png)"
        )
        if file_name:
            self.set_image(file_name)

    def set_image(self, image):
        self.pixmap = image
        self.image_label.setPixmap(
            self.pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
        )

    def get_image(self):
        return self.pixmap
