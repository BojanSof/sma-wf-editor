from enum import Enum
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QColor, QPen, QPainterPath
from PySide6.QtCore import Qt


class WatchFaceImage(QGraphicsPixmapItem):
    class HorizontalAlignment(Enum):
        Left = 0
        Center = 1
        Right = 2

    def __init__(
        self, pixmap, x=0, y=0, resizable=True, movable=True, selectable=True, h_align=HorizontalAlignment.Left
    ):
        super().__init__(pixmap)
        self.original_pixmap = pixmap
        self.setAcceptHoverEvents(True)
        self.h_align = h_align
        offset_x = 0
        if self.h_align == WatchFaceImage.HorizontalAlignment.Center:
            offset_x = pixmap.width() // 2
        elif self.h_align == WatchFaceImage.HorizontalAlignment.Right:
            offset_x = pixmap.width()
        self.setOffset(-offset_x, 0)
        self.setPos(x, y)
        self.resizing = False
        self.resize_handle_size = 10
        self.resize_handle = None
        self.resize_enabled = resizable
        self.move_enabled = movable
        self.select_enabled = selectable
        self.setFlag(
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges,
            movable,
        )
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, selectable)
        if self.resize_enabled:
            self.create_resize_handle()
            self.resize_handle.setVisible(False)

    def create_resize_handle(self):
        if self.resize_handle:
            self.scene().removeItem(self.resize_handle)

        rect = self.boundingRect()
        x, y = (
            rect.right() - self.resize_handle_size,
            rect.bottom() - self.resize_handle_size,
        )
        self.resize_handle = QGraphicsRectItem(x, y, self.resize_handle_size, self.resize_handle_size, self)
        self.resize_handle.setBrush(QColor(255, 0, 0, 150))
        self.resize_handle.setPen(QPen(Qt.PenStyle.NoPen))

    def hoverMoveEvent(self, event):
        if self.resize_enabled:
            if self.resize_handle.contains(event.pos()):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if self.resize_enabled:
            if self.resize_handle.contains(event.pos()):
                self.resizing = True
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.resizing = False
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_width = event.pos().x()
            new_height = event.pos().y()
            scene_rect = self.scene().sceneRect()
            item_rect = self.mapToScene(self.boundingRect()).boundingRect()

            # Limit the resizing to be within the scene bounds
            if item_rect.left() + new_width > scene_rect.right():
                new_width = scene_rect.right() - item_rect.left()
            if item_rect.top() + new_height > scene_rect.bottom():
                new_height = scene_rect.bottom() - item_rect.top()

            if new_width > self.resize_handle_size and new_height > self.resize_handle_size:
                self.setPixmap(self.original_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio))
                self.create_resize_handle()
                self.resize_handle.setVisible(True)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def setSelected(self, selected):
        super().setSelected(selected)
        if self.resize_enabled:
            self.resize_handle.setVisible(selected)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange and self.resize_enabled:
            self.resize_handle.setVisible(value)
        elif change == QGraphicsItem.ItemPositionChange and self.scene():
            rect = self.scene().sceneRect()
            width = self.boundingRect().width()
            height = self.boundingRect().height()
            # Keep the item inside the scene rect
            if value.x() < rect.left():
                value.setX(rect.left())
            elif value.x() + width > rect.right():
                value.setX(rect.right() - width)
            if value.y() < rect.top():
                value.setY(rect.top())
            elif value.y() + height > rect.bottom():
                value.setY(rect.bottom() - height)
            return value
        return super().itemChange(change, value)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path