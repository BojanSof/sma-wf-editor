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
        self.init_params()
        self.init_wf_editor()
        self.init_actions()

    def init_params(self):
        self.width = 410
        self.height = 502
        self.leWidth.setText(str(self.width))
        self.leHeight.setText(str(self.height))

    def init_wf_editor(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.view.setScene(self.scene)

        self.image_items = []
        self.layer_items = []

        self.lwWfLayers.itemSelectionChanged.connect(self.on_layer_selection_changed)
        self.scene.selectionChanged.connect(self.on_image_selection_changed)

        self.preview_dialog = PreviewDialog()

    def init_actions(self):
        self.btnAddLayer.clicked.connect(self.add_layer)
        self.btnRemoveLayer.clicked.connect(self.remove_layer)
        self.btnRemoveAllLayers.clicked.connect(self.remove_all_layers)
        self.actionLoadWf.triggered.connect(self.load_watch_face)
        self.actionSaveWf.triggered.connect(self.save_watch_face)
        self.actionExit.triggered.connect(self.close)
        self.actionPreview.triggered.connect(self.preview_watch_face)

    def add_layer(self):
        block_info = BlockInfo(0, 0, 0, 0, 0, 0, 0, False, BlockType.Preview, BlockHorizontalAlignment.Left, 0, 0, 0)
        self.create_layer(block_info, [], 0, 0, 0, 0)

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

    def remove_all_layers(self):
        self.layer_items.clear()
        self.lwWfLayers.clear()
        self.image_items.clear()
        self.scene.clear()

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
        self.remove_all_layers()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Watch Face File", "", "Bin Files (*.bin)")
        if file_name:
            with open(file_name, "rb") as f:
                wf_data = f.read()
            watch_face = WatchFace.loads(wf_data)
            self.image_items.clear()
            for bi in watch_face.meta_data.blocks_info:
                images = [
                    watch_face.imgs_data[bi.img_id + i_img].unpack()
                    for i_img in range(bi.num_imgs)
                ]
                self.create_layer(bi, images)
    
    def create_watch_face(self):
        blocks_info = []
        imgs_data = []
        img_offset = 0
        for layer in self.layer_items:
            bi = layer.block_info
            layer_images = layer.get_images()
            for img in layer_images:
                img_data = ImageData.pack(img, bi.compr)
                imgs_data.append(img_data)
                img_offset += len(bytes(img_data))
            bi.img_offset = img_offset
            blocks_info.append(bi)
        imgs_size_info = [len(bytes(img_data)) for img_data in imgs_data]
        header = WatchFaceHeader(len(imgs_data), len(blocks_info), 2)
        metadata = WatchFaceMetaData(header, blocks_info, imgs_size_info)
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

    def on_layer_selection_changed(self):
        selected_items = self.lwWfLayers.selectedItems()
        selected_indices = [self.lwWfLayers.row(item) for item in selected_items]
        for i, img_item in enumerate(self.image_items):
            img_item.setSelected(i in selected_indices)

    def on_image_selection_changed(self):
        selected_items = self.scene.selectedItems()
        selected_indices = [self.image_items.index(item) for item in selected_items if item in self.image_items]

        self.lwWfLayers.blockSignals(True)
        self.lwWfLayers.clearSelection()
        for index in selected_indices:
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
