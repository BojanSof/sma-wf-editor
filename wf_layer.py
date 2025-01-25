from PySide6.QtWidgets import (
    QListWidgetItem,
    QLabel,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QFileDialog,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QStyledItemDelegate,
    QStyle,
    QMessageBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from wf_image import WatchFaceImage
from smawf import BlockHorizontalAlignment, BlockType, BlockInfo, arm_block_types


class IconOnlyDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected or option.state & QStyle.State_MouseOver:
            painter.save()
            painter.setBrush(option.palette.highlight())
            painter.setPen(Qt.NoPen)
            painter.drawRect(option.rect)
            painter.restore()

        icon = index.data(Qt.DecorationRole)
        if icon:
            rect = option.rect
            size = option.decorationSize
            icon_rect = rect.adjusted(
                (rect.width() - size.width()) // 2,
                (rect.height() - size.height()) // 2,
                -(rect.width() - size.width()) // 2,
                -(rect.height() - size.height()) // 2,
            )
            icon.paint(painter, icon_rect, alignment=Qt.AlignCenter)


class WatchFaceLayer(QListWidgetItem):
    def __init__(
        self,
        img_item: WatchFaceImage,
        block_info: BlockInfo,
        images: list[QPixmap],
        max_x=1000,
        max_y=1000,
        rot_x=0,
        rot_y=0,
        parent=None,
    ):
        super().__init__(parent)

        self.image_item = img_item
        self.block_info = block_info
        self.images = images

        self.widget = QWidget()
        self.image_combobox = QComboBox()
        self.image_combobox.setFixedSize(100, 100)
        self.image_combobox.setIconSize(QSize(70, 70))
        self.image_combobox.setItemDelegate(IconOnlyDelegate(self.image_combobox))
        self.update_image_combobox()
        self.image_combobox.currentIndexChanged.connect(self.update_image)

        self.type_field = QComboBox()
        self.type_field.addItems([str(t) for t in BlockType])
        self.type_field.setCurrentText(str(block_info.blocktype))
        self.type_field.currentIndexChanged.connect(self.update_info)

        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(10, max_x)
        self.width_spinbox.setValue(block_info.width)
        self.width_spinbox.setMaximumWidth(70)
        self.width_spinbox.valueChanged.connect(self.update_width)

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(10, max_y)
        self.height_spinbox.setValue(block_info.height)
        self.height_spinbox.setMaximumWidth(70)
        self.height_spinbox.valueChanged.connect(self.update_height)

        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, max_x)
        self.x_spinbox.setValue(block_info.pos_x)
        self.x_spinbox.setMaximumWidth(70)
        self.x_spinbox.valueChanged.connect(self.update_info)

        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, max_y)
        self.y_spinbox.setValue(block_info.pos_y)
        self.y_spinbox.setMaximumWidth(70)
        self.y_spinbox.valueChanged.connect(self.update_info)

        self.rotation_spinbox = QSpinBox()
        self.rotation_spinbox.setRange(0, 360)
        self.rotation_spinbox.setMaximumWidth(70)
        self.rotation_spinbox.setWrapping(True)
        self.rotation_spinbox.valueChanged.connect(self.update_info)

        self.rot_x_spinbox = QSpinBox()
        self.rot_x_spinbox.setRange(0, max_x)
        self.rot_x_spinbox.setValue(rot_x)
        self.rot_x_spinbox.setMaximumWidth(70)
        self.rot_x_spinbox.valueChanged.connect(self.update_info)

        self.rot_y_spinbox = QSpinBox()
        self.rot_y_spinbox.setRange(0, max_y)
        self.rot_y_spinbox.setValue(rot_y)
        self.rot_y_spinbox.setMaximumWidth(70)
        self.rot_y_spinbox.valueChanged.connect(self.update_info)

        self.align_map = {
            BlockHorizontalAlignment.NotSpecified: "Not specified",
            BlockHorizontalAlignment.Left: "Left",
            BlockHorizontalAlignment.Center: "Center",
            BlockHorizontalAlignment.Right: "Right",
        }
        self.align_combobox = QComboBox()
        self.align_combobox.addItems(list(self.align_map.values()))
        self.align_combobox.setCurrentText(self.align_map[block_info.align])
        self.align_combobox.currentIndexChanged.connect(self.update_info)
        self.align_combobox.setMaximumWidth(70)

        self.num_images_lineedit = QLineEdit()
        self.num_images_lineedit.setReadOnly(True)
        self.num_images_lineedit.setText(str(block_info.num_imgs))
        self.num_images_lineedit.setMaximumWidth(70)

        self.compression_combobox = QComboBox()
        self.compression_combobox.addItems(["0x00", "0x04"])
        if block_info.compr == 0x00:
            self.compression_combobox.setCurrentIndex(0)
        elif block_info.compr == 0x04:
            self.compression_combobox.setCurrentIndex(1)
        self.compression_combobox.currentIndexChanged.connect(self.update_info)
        self.compression_combobox.setMaximumWidth(70)

        self.rgba_checkbox = QCheckBox("RGBA")
        self.rgba_checkbox.setChecked(block_info.is_rgba)
        self.rgba_checkbox.stateChanged.connect(self.update_info)

        self.load_button = QPushButton("Load Images")
        self.load_button.clicked.connect(self.load_image)

        preview_type_layout = QHBoxLayout()
        preview_type_layout.addWidget(self.image_combobox)
        preview_type_layout.addWidget(self.type_field)

        options_layout = QGridLayout()
        spacer = QSpacerItem(30, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        options_layout.addItem(spacer, 0, 2)
        row = 0
        options_layout.addWidget(QLabel("Width:"), row, 0)
        options_layout.addWidget(self.width_spinbox, row, 1)
        options_layout.addWidget(QLabel("X:"), row, 3)
        options_layout.addWidget(self.x_spinbox, row, 4)
        row += 1
        options_layout.addWidget(QLabel("Height:"), 1, 0)
        options_layout.addWidget(self.height_spinbox, 1, 1)
        options_layout.addWidget(QLabel("Y:"), 1, 3)
        options_layout.addWidget(self.y_spinbox, 1, 4)
        self.rotation_elements = [
            QLabel("Rot X:"),
            self.rot_x_spinbox,
            QLabel("Rotation:"),
            self.rotation_spinbox,
            QLabel("Rot Y:"),
            self.rot_y_spinbox,
        ]
        row += 1
        options_layout.addWidget(self.rotation_elements[0], row, 0)
        options_layout.addWidget(self.rotation_elements[1], row, 1)
        options_layout.addWidget(self.rotation_elements[2], row, 3)
        options_layout.addWidget(self.rotation_elements[3], row, 4)
        row += 1
        options_layout.addWidget(self.rotation_elements[4], row, 0)
        options_layout.addWidget(self.rotation_elements[5], row, 1)
        row += 1
        options_layout.addWidget(QLabel("Alignment:"), row, 0)
        options_layout.addWidget(self.align_combobox, row, 1, 1, 1)
        row += 1
        options_layout.addWidget(QLabel("Compression:"), row, 0)
        options_layout.addWidget(self.compression_combobox, row, 1)
        options_layout.addWidget(self.rgba_checkbox, row, 4)
        row += 1
        options_layout.addWidget(QLabel("Num Images:"), row, 0)
        options_layout.addWidget(self.num_images_lineedit, row, 1)
        options_layout.addWidget(self.load_button, row, 4)

        main_layout = QVBoxLayout()
        main_layout.addLayout(preview_type_layout)
        main_layout.addLayout(options_layout)

        self.widget.setLayout(main_layout)
        self.setSizeHint(self.widget.sizeHint())

        rot_elements_visible = block_info.blocktype in arm_block_types
        for rot_element in self.rotation_elements:
            rot_element.setVisible(rot_elements_visible)

        self.pixmap = None
        if len(images) > 0:
            self.update_image()

    def update_image_combobox(self):
        self.image_combobox.clear()
        for i, img in enumerate(self.images):
            icon = QIcon(img)
            self.image_combobox.addItem(icon, "")

    def update_image(self):
        current_index = self.image_combobox.currentIndex()
        if current_index >= 0 and current_index < len(self.images):
            self.pixmap = self.images[current_index]
            self.image_combobox.setItemIcon(self.image_combobox.currentIndex(), QIcon(self.pixmap))
            self.image_item.setNewPixmap(
                self.images[current_index].scaled(self.block_info.width, self.block_info.height, Qt.KeepAspectRatio)
            )

    def load_image(self):
        file_names, _ = QFileDialog.getOpenFileNames(self.widget, "Open Image File", "", "Images (*.png)")
        if file_names:
            self.images.clear()
            images = [QPixmap(file_name) for file_name in file_names]
            if not all(img.width() == images[0].width() and img.height() == images[0].height() for img in images):
                QMessageBox.critical(
                    self, "Image size mismatch", "All images must have the same width and height", QMessageBox.Ok
                )
                return
            for file_name in file_names:
                self.images.append(QPixmap(file_name))
            self.width_spinbox.blockSignals(True)
            self.height_spinbox.blockSignals(True)
            self.width_spinbox.setValue(images[0].width())
            self.height_spinbox.setValue(images[0].height())
            self.width_spinbox.blockSignals(False)
            self.height_spinbox.blockSignals(False)
            self.update_image_combobox()
            self.update_info()
            self.update_image()

    def get_image(self):
        return self.pixmap

    def update_width(self):
        if not self.image_item.pixmap().isNull():
            aspect_ratio = self.image_item.pixmap().height() / self.image_item.pixmap().width()
            new_width = self.width_spinbox.value()
            new_height = round(new_width * aspect_ratio)
            self.height_spinbox.setValue(new_height)
            self.height_spinbox.blockSignals(False)
        self.update_info()

    def update_height(self):
        if not self.image_item.pixmap().isNull():
            aspect_ratio = self.image_item.pixmap().width() / self.image_item.pixmap().height()
            new_height = self.height_spinbox.value()
            new_width = round(new_height * aspect_ratio)
            self.width_spinbox.blockSignals(True)
            self.width_spinbox.setValue(new_width)
            self.width_spinbox.blockSignals(False)
        self.update_info()

    def update_info(self):
        self.block_info.blocktype = BlockType[self.type_field.currentText()]
        is_arm_block = self.block_info.blocktype in arm_block_types
        for rot_element in self.rotation_elements:
            rot_element.setVisible(is_arm_block)
        self.image_item.setRotatable(is_arm_block)
        if self.block_info.blocktype == BlockType.Background:
            self.image_item.setMovable(False)
            self.image_item.setResizable(False)
        else:
            self.image_item.setMovable(True)
            self.image_item.setResizable(True)
        self.block_info.width = self.width_spinbox.value()
        self.block_info.height = self.height_spinbox.value()
        self.block_info.pos_x = self.x_spinbox.value()
        self.block_info.pos_y = self.y_spinbox.value()
        self.reverse_align_map = {v: k for k, v in self.align_map.items()}
        self.block_info.align = self.reverse_align_map[self.align_combobox.currentText()]
        self.block_info.compr = 0 if self.compression_combobox.currentIndex() == 0 else 4
        self.block_info.is_rgba = self.rgba_checkbox.isChecked()
        self.block_info.num_imgs = len(self.images)
        if self.pixmap is not None:
            self.image_item.setPos(self.block_info.pos_x, self.block_info.pos_y)
            self.image_item.setPixmap(
                self.pixmap.scaled(self.block_info.width, self.block_info.height, Qt.KeepAspectRatio)
            )
            self.image_item.setRotation(self.rotation_spinbox.value())

    def set_position(self, x, y):
        self.x_spinbox.setValue(x)
        self.y_spinbox.setValue(y)

    def set_size(self, width, height):
        self.width_spinbox.setValue(width)
        self.height_spinbox.setValue(height)

    def set_rotation(self, rotation):
        self.rotation_spinbox.setValue(rotation)

    def set_max_coordinates(self, max_x, max_y):
        self.width_spinbox.setRange(0, max_x)
        self.height_spinbox.setRange(0, max_y)
        self.x_spinbox.setRange(0, max_x)
        self.y_spinbox.setRange(0, max_y)
        self.rot_x_spinbox.setRange(0, max_x)
        self.rot_y_spinbox.setRange(0, max_y)
