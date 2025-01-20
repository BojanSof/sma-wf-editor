import sys

from PySide6.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog
from PySide6.QtGui import QPixmap
from PIL.ImageQt import ImageQt

from wf_creator_window import Ui_MainWindow as SmaWfCreatorWindow
from wf_image import WatchFaceImage
from wf_layer import WatchFaceLayer

from smawf import BlockHorizontalAlignment, WatchFace, arm_block_types


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

    def init_actions(self):
        self.actionLoadWf.triggered.connect(self.load_watch_face)
        self.actionSaveWf.triggered.connect(self.save_watch_face)
        self.actionExit.triggered.connect(self.close)
        self.actionPreview.triggered.connect(self.preview_watch_face)

    def load_watch_face(self):
        self.lwWfLayers.clear()
        self.image_items.clear()
        self.scene.clear()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Watch Face File", "", "Bin Files (*.bin)")
        if file_name:
            with open(file_name, "rb") as f:
                wf_data = f.read()
            self.watch_face = WatchFace.loads(wf_data)
            self.image_items.clear()
            for i, bi in enumerate(self.watch_face.meta_data.blocks_info):
                # print(f"Block {i}: {bi}")
                images = [
                    QPixmap.fromImage(ImageQt(self.watch_face.imgs_data[bi.img_id + i_img].unpack()))
                    for i_img in range(bi.num_imgs)
                ]
                if bi.blocktype in arm_block_types:
                    origin_x = bi.width - bi.cent_y
                    origin_y = bi.height - bi.cent_x
                    x = bi.pos_x
                    y = bi.pos_y
                    rotate_enabled = True
                else:
                    origin_x = 0
                    origin_y = 0
                    x = bi.pos_x
                    y = bi.pos_y
                    rotate_enabled = False
                if bi.align == BlockHorizontalAlignment.Center:
                    origin_x = bi.width // 2
                elif bi.align == BlockHorizontalAlignment.Right:
                    origin_x = bi.width
                layer = WatchFaceLayer(
                    bi, images=images, max_x=self.width, max_y=self.height, rot_x=origin_x, rot_y=origin_y
                )
                self.lwWfLayers.addItem(layer)
                self.lwWfLayers.setItemWidget(layer, layer.widget)
                img = WatchFaceImage(
                    layer.get_image(),
                    x=x,
                    y=y,
                    origin_x=origin_x,
                    origin_y=origin_y,
                    rotatable=rotate_enabled,
                )
                img.positionChanged.connect(layer.set_position)
                img.sizeChanged.connect(layer.set_size)
                img.rotationChanged.connect(layer.set_rotation)
                self.image_items.append(img)
                self.scene.addItem(img)
                layer.image_item = img
                self.layer_items.append(layer)

    def save_watch_face(self):
        print("Save Watch Face")

    def preview_watch_face(self):
        print("Preview Watch Face")

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
