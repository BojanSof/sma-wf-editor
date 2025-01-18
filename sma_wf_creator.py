import sys

from PySide6.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog
from PySide6.QtGui import QPixmap
from PIL.ImageQt import ImageQt

from wf_creator_window import Ui_MainWindow as SmaWfCreatorWindow
from wf_image import WatchFaceImage
from wf_layer import WatchFaceLayer

from smawf import BlockHorizontalAlignment, BlockType, WatchFace


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
        # for i in range(12):
        #     item = WatchFaceLayer(name=f"Layer {i}", image_path=f"watch_faces/10011_blue/{i:03d}.png")
        #     self.lwWfLayers.addItem(item)
        #     self.lwWfLayers.setItemWidget(item, item.widget)
        #     wf_image = WatchFaceImage(item.get_image())
        #     self.scene.addItem(wf_image)
        #     self.image_items.append(wf_image)

        self.lwWfLayers.itemSelectionChanged.connect(self.on_layer_selection_changed)
        self.scene.selectionChanged.connect(self.on_image_selection_changed)

    def init_actions(self):
        self.actionLoadWf.triggered.connect(self.load_watch_face)
        self.actionSaveWf.triggered.connect(self.save_watch_face)
        self.actionExit.triggered.connect(self.close)

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
                print(f"Block {i}: {bi}")
                img_data = self.watch_face.imgs_data[bi.img_id].unpack()
                layer = WatchFaceLayer(name=f"Layer {i}", image=QPixmap.fromImage(ImageQt(img_data)))
                self.lwWfLayers.addItem(layer)
                self.lwWfLayers.setItemWidget(layer, layer.widget)
                h_align_map = {
                    BlockHorizontalAlignment.Left: WatchFaceImage.HorizontalAlignment.Left,
                    BlockHorizontalAlignment.Center: WatchFaceImage.HorizontalAlignment.Center,
                    BlockHorizontalAlignment.Right: WatchFaceImage.HorizontalAlignment.Right,
                }
                h_align = h_align_map[bi.align] if bi.align in h_align_map else WatchFaceImage.HorizontalAlignment.Left
                if bi.blocktype in [BlockType.HoursArm, BlockType.MinutesArm, BlockType.SecondsArm]:
                    x = bi.pos_x - bi.width + bi.cent_y
                    y = bi.pos_y - bi.height + bi.cent_x
                else:
                    x = bi.pos_x
                    y = bi.pos_y
                img = WatchFaceImage(layer.get_image(), x=x, y=y, h_align=h_align)
                self.image_items.append(img)
                self.scene.addItem(img)

    def save_watch_face(self):
        print("Save Watch Face")

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
