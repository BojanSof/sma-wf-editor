import json
import os
import sys

from PySide6.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog, QMessageBox

from wf_creator_window import Ui_MainWindow as SmaWfCreatorWindow
from wf_image import WatchFaceImage
from wf_layer import WatchFaceLayer
from wf_preview_dialog import PreviewDialog

from smawf import get_origin_point

from smawf import (
    BlockHorizontalAlignment,
    BlockType,
    BlockInfo,
    WatchFace,
    WatchFaceMetaData,
    Header as WatchFaceHeader,
    ImageData,
)


class SmaWfCreator(QMainWindow, SmaWfCreatorWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_config()
        self.init_actions()
        self.init_wf_editor()
        self.change_device("Custom Device")

    def init_config(self):
        self.devices = ["Custom Device"]
        self.width = 410
        self.height = 502
        if os.path.exists("devices.json"):
            with open("devices.json") as f:
                self.devices = json.load(f)

    def init_actions(self):
        self.comboDevice.addItems([dev["name"] for dev in self.devices])
        self.comboDevice.currentTextChanged.connect(self.change_device)
        self.spinboxWidth.valueChanged.connect(self.update_wf_editor)
        self.spinboxHeight.valueChanged.connect(self.update_wf_editor)
        self.btnAddLayer.clicked.connect(self.add_layer)
        self.btnRemoveLayer.clicked.connect(self.remove_layer)
        self.btnRemoveAllLayers.clicked.connect(self.remove_all_layers)
        self.btnMoveLayerUp.clicked.connect(self.move_layer_up)
        self.btnMoveLayerDown.clicked.connect(self.move_layer_down)
        self.actionLoadWf.triggered.connect(self.load_watch_face)
        self.actionSaveWf.triggered.connect(self.save_watch_face)
        self.actionExit.triggered.connect(self.close)
        self.actionPreview.triggered.connect(self.preview_watch_face)
        self.actionSaveImages.triggered.connect(self.save_all_images)

    def init_wf_editor(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.view.setScene(self.scene)

        self.image_items = []
        self.layer_items = []

        self.lwWfLayers.itemSelectionChanged.connect(self.on_layer_selection_changed)
        self.scene.selectionChanged.connect(self.on_image_selection_changed)

        self.preview_dialog = PreviewDialog()

    def change_device(self, dev_name):
        device = [dev for dev in self.devices if dev["name"] == dev_name][0]
        if device["name"] == "Custom Device":
            self.spinboxWidth.setEnabled(True)
            self.spinboxHeight.setEnabled(True)
            self.width = 410
            self.height = 502
        else:
            self.spinboxWidth.setEnabled(False)
            self.spinboxHeight.setEnabled(False)
            self.width = device["width"]
            self.height = device["height"]
        self.spinboxWidth.blockSignals(True)
        self.spinboxHeight.blockSignals(True)
        self.spinboxWidth.setValue(self.width)
        self.spinboxHeight.setValue(self.height)
        self.spinboxWidth.blockSignals(False)
        self.spinboxHeight.blockSignals(False)

    def update_wf_editor(self):
        self.width = self.spinboxWidth.value()
        self.height = self.spinboxHeight.value()
        self.scene.setSceneRect(0, 0, self.width, self.height)

    def add_layer(self):
        block_info = BlockInfo(0, 0, 0, 0, 0, 0, 0, False, BlockType.Preview, BlockHorizontalAlignment.Left, 0x04, 0, 0)
        self.create_layer(block_info, [])
        if len(self.layer_items) > 0:
            self.gbParams.setEnabled(False)
        self.select_layer(self.lwWfLayers.count() - 1)
        self.on_layer_selection_changed()

    def remove_layer(self):
        selected_items = self.lwWfLayers.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.lwWfLayers.row(item)
            self.lwWfLayers.takeItem(row)
            image_item = self.image_items.pop(row)
            self.scene.removeItem(image_item)
            self.layer_items.pop(row)
        if len(self.layer_items) == 0:
            self.gbParams.setEnabled(True)

    def remove_all_layers(self):
        self.layer_items.clear()
        self.lwWfLayers.clear()
        self.image_items.clear()
        self.scene.clear()
        self.gbParams.setEnabled(True)

    def move_layer_up(self):
        row = self.lwWfLayers.currentRow()
        if row < 1:
            return
        self.lwWfLayers.blockSignals(True)
        widget = self.lwWfLayers.itemWidget(self.lwWfLayers.currentItem())
        item = self.lwWfLayers.currentItem().clone()
        self.lwWfLayers.insertItem(row - 1, item)
        self.lwWfLayers.setItemWidget(item, widget)
        self.lwWfLayers.takeItem(row + 1)
        self.lwWfLayers.setCurrentRow(row - 1)
        self.lwWfLayers.blockSignals(False)
        self.layer_items[row], self.layer_items[row - 1] = self.layer_items[row - 1], self.layer_items[row]
        self.image_items[row], self.image_items[row - 1] = self.image_items[row - 1], self.image_items[row]
        self.image_items[row - 1].stackBefore(self.image_items[row])
        self.scene.update()

    def move_layer_down(self):
        row = self.lwWfLayers.currentRow()
        if row == -1 or row == self.lwWfLayers.count() - 1:
            return
        self.lwWfLayers.blockSignals(True)
        widget = self.lwWfLayers.itemWidget(self.lwWfLayers.currentItem())
        item = self.lwWfLayers.currentItem().clone()
        self.lwWfLayers.insertItem(row + 2, item)
        self.lwWfLayers.setItemWidget(item, widget)
        self.lwWfLayers.takeItem(row)
        self.lwWfLayers.setCurrentRow(row + 1)
        self.lwWfLayers.blockSignals(False)
        self.layer_items[row], self.layer_items[row + 1] = self.layer_items[row + 1], self.layer_items[row]
        self.image_items[row], self.image_items[row + 1] = self.image_items[row + 1], self.image_items[row]
        self.image_items[row].stackBefore(self.image_items[row + 1])
        self.scene.update()

    def create_layer(self, block_info, images):
        origin_x, origin_y = get_origin_point(block_info)
        x, y = block_info.pos_x, block_info.pos_y
        img = WatchFaceImage(
            None,
            x=x,
            y=y,
            origin_x=origin_x,
            origin_y=origin_y,
        )
        layer = WatchFaceLayer(img, block_info, images, self.width, self.height)
        img.positionChanged.connect(layer.set_position)
        img.sizeChanged.connect(layer.set_size)
        img.rotationChanged.connect(layer.set_rotation)
        self.lwWfLayers.addItem(layer)
        self.lwWfLayers.setItemWidget(layer, layer.widget)
        self.image_items.append(img)
        self.scene.addItem(img)
        self.layer_items.append(layer)
        layer.update_info()

    def load_watch_face(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Watch Face File", "", "Bin Files (*.bin)")
        if file_name:
            self.remove_all_layers()
            with open(file_name, "rb") as f:
                wf_data = f.read()
            watch_face = WatchFace.loads(wf_data)
            self.image_items.clear()
            for bi in watch_face.meta_data.blocks_info:
                images = [watch_face.imgs_data[bi.img_id + i_img].unpack() for i_img in range(bi.num_imgs)]
                self.create_layer(bi, images)
            self.gbParams.setEnabled(False)

    def create_watch_face(self):
        blocks_info = []
        imgs_data = []
        img_offset = 0
        img_id = 0
        for layer in self.layer_items:
            bi = layer.block_info
            bi.img_offset = img_offset
            bi.img_id = img_id
            layer_images = layer.get_images()
            for img in layer_images:
                img_data = ImageData.pack(img, bi.compr)
                imgs_data.append(img_data)
                img_offset += len(bytes(img_data))
            img_id += len(layer_images)
            blocks_info.append(bi)
        imgs_size_info = [len(bytes(img_data)) for img_data in imgs_data]
        header = WatchFaceHeader(len(imgs_data), len(blocks_info), 2)
        # adjust img offsets
        metadata = WatchFaceMetaData(header, blocks_info, imgs_size_info)
        for bi in blocks_info:
            bi.img_offset += len(bytes(metadata))
        return WatchFace(metadata, imgs_data)

    def save_watch_face(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Open Watch Face File", "", "Bin Files (*.bin)")
        if file_name:
            with open(file_name, "wb") as f:
                wf = self.create_watch_face()
                f.write(bytes(wf))
            QMessageBox.information(self, "Save Watch Face", "Watch Face saved successfully")

    def preview_watch_face(self):
        wf = self.create_watch_face()
        preview = wf.preview(self.width, self.height)
        self.preview_dialog.set_gif(preview)
        self.preview_dialog.show()

    def save_all_images(self):
        save_dir = QFileDialog.getExistingDirectory(self, "Open folder to save images")
        if save_dir:
            wf = self.create_watch_face()
            for bi in wf.meta_data.blocks_info:
                for i_img in range(bi.img_id, bi.img_id + bi.num_imgs):
                    img = wf.imgs_data[i_img].unpack()
                    img_name = str(bi.blocktype) + f"_{i_img - bi.img_id:02d}.png"
                    img.save(os.path.join(save_dir, img_name))
            QMessageBox.information(self, "Save Watch Face Images", "Watch Face images saved successfully")

    def on_layer_selection_changed(self):
        selected_items = self.lwWfLayers.selectedItems()
        selected_indices = [self.lwWfLayers.row(item) for item in selected_items]
        for i, img_item in enumerate(self.image_items):
            img_item.setSelected(i in selected_indices)

    def on_image_selection_changed(self):
        selected_items = self.scene.selectedItems()
        selected_indices = [self.image_items.index(item) for item in selected_items if item in self.image_items]
        for index in selected_indices:
            self.select_layer(index)
    
    def select_layer(self, index):
        self.lwWfLayers.blockSignals(True)
        self.lwWfLayers.clearSelection()
        self.lwWfLayers.item(index).setSelected(True)
        self.lwWfLayers.scrollToItem(self.lwWfLayers.item(index))
        self.lwWfLayers.blockSignals(False)


def main():
    app = QApplication(sys.argv)
    wf_creator = SmaWfCreator()
    wf_creator.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
