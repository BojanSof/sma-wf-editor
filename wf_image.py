import math

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem, QGraphicsEllipseItem
from PySide6.QtGui import QColor, QPen, QPainterPath
from PySide6.QtCore import Qt, Signal, QObject


class WatchFaceImage(QGraphicsPixmapItem, QObject):
    positionChanged = Signal(float, float)
    sizeChanged = Signal(int, int)
    rotationChanged = Signal(float)

    def __init__(
        self,
        pixmap,
        x=0,
        y=0,
        origin_x=0,
        origin_y=0,
        resizable=True,
        movable=True,
        selectable=True,
        rotatable=True,
    ):
        QGraphicsPixmapItem.__init__(self, pixmap)
        QObject.__init__(self)
        self.original_pixmap = pixmap
        self.setAcceptHoverEvents(True)
        self.setOffset(-origin_x, -origin_y)
        self.setPos(x, y)
        self.resizing = False
        self.resize_handle_size = 10
        self.rotating = False
        self.rotate_origin_size = 10

        self.resize_handle = None
        self.rotate_origin = None
        self.create_resize_handle()
        self.create_rotate_origin()

        self.setSelectable(selectable)
        self.setMovable(movable)
        self.setResizable(resizable)
        self.setRotatable(rotatable)

        if self.resize_handle:
            self.resize_handle.setVisible(False)
        if self.rotate_origin:
            self.rotate_origin.setVisible(False)

    def setPixmap(self, pixmap):
        if self.pixmap().isNull():
            super().setPixmap(pixmap)
        else:
            old_width = self.pixmap().width()
            old_height = self.pixmap().height()
            new_width = pixmap.width()
            new_height = pixmap.height()
            super().setPixmap(pixmap)
            scale_x = new_width / old_width
            scale_y = new_height / old_height
            self.setOffset(self.offset().x() * scale_x, self.offset().y() * scale_y)
        self.update_transform_handles()

    def setNewPixmap(self, pixmap):
        self.original_pixmap = pixmap
        super().setPixmap(pixmap)
        self.update_transform_handles()

    def setSelectable(self, selectable):
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, selectable)
        self.select_enabled = selectable

    def setMovable(self, movable):
        self.move_enabled = movable
        self.setFlag(
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges,
            movable,
        )

    def setResizable(self, resizable):
        self.resize_enabled = resizable
        if self.resize_enabled:
            self.update_resize_handle()
        else:
            if self.resize_handle and self.resize_handle.scene():
                self.resize_handle.scene().removeItem(self.resize_handle)

    def setRotatable(self, rotatable):
        self.rotate_enabled = rotatable
        if self.rotate_enabled:
            self.update_rotate_origin()
        else:
            if self.rotate_origin and self.rotate_origin.scene():
                self.rotate_origin.scene().removeItem(self.rotate_origin)

    def setRotation(self, angle):
        super().setRotation(angle)
        self.update_transform_handles()
    
    def create_resize_handle(self):
        if self.resize_handle and self.resize_handle.scene():
            self.resize_handle.scene().removeItem(self.resize_handle)
        rect = self.boundingRect()
        x, y = (
            rect.right() - self.resize_handle_size,
            rect.bottom() - self.resize_handle_size,
        )
        self.resize_handle = QGraphicsRectItem(x, y, self.resize_handle_size, self.resize_handle_size, self)
        self.resize_handle.setBrush(QColor(255, 0, 0, 200))
        self.resize_handle.setPen(QPen(Qt.PenStyle.NoPen))

    def create_rotate_origin(self):
        if self.rotate_origin and self.rotate_origin.scene():
            self.rotate_origin.scene().removeItem(self.rotate_origin)
        x = self.transformOriginPoint().x() - self.rotate_origin_size // 2
        y = self.transformOriginPoint().y() - self.rotate_origin_size // 2
        self.rotate_origin = QGraphicsEllipseItem(x, y, self.rotate_origin_size, self.rotate_origin_size, self)
        self.rotate_origin.setBrush(QColor(0, 255, 0, 200))
        self.rotate_origin.setPen(QPen(Qt.PenStyle.NoPen))

    def update_resize_handle(self):
        if self.resize_enabled:
            visible = self.isSelected()
            self.create_resize_handle()
            self.resize_handle.setVisible(visible)

    def update_rotate_origin(self):
        if self.rotate_enabled:
            visible = self.isSelected()
            self.create_rotate_origin()
            self.rotate_origin.setVisible(visible)

    def update_transform_handles(self):
        self.update_resize_handle()
        self.update_rotate_origin()

    def hoverMoveEvent(self, event):
        if self.resize_enabled:
            if self.resize_handle.contains(event.pos()):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if self.resize_enabled:
            if self.resize_handle.contains(event.pos()):
                self.initial_resize_pos = event.scenePos()
                self.initial_width = self.pixmap().width()
                self.initial_height = self.pixmap().height()
                self.resizing = True
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.resizing = False
                self.setCursor(Qt.CursorShape.OpenHandCursor)
        if self.rotate_enabled:
            if self.rotating and event.button() == Qt.LeftButton:
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.initial_rotation_pos = event.scenePos()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.rotate_enabled:
            if event.button() == Qt.LeftButton:
                self.rotating = not self.rotating
                if self.rotating:
                    self.setCursor(Qt.CursorShape.CrossCursor)
                else:
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.scenePos() - self.initial_resize_pos
            new_width = self.initial_width + delta.x()
            new_height = self.initial_height + delta.y()
            scene_rect = self.scene().sceneRect()
            item_rect = self.mapToScene(self.boundingRect()).boundingRect()

            # Limit the resizing to be within the scene bounds
            if item_rect.left() + new_width > scene_rect.right():
                new_width = scene_rect.right() - item_rect.left()
            if item_rect.top() + new_height > scene_rect.bottom():
                new_height = scene_rect.bottom() - item_rect.top()
            if new_width > self.resize_handle_size and new_height > self.resize_handle_size:
                self.setPixmap(self.original_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio))
                self.sizeChanged.emit(new_width, new_height)
        elif self.rotating and event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.scenePos()
            center_pos = self.mapToScene(self.boundingRect().center())
            angle = math.degrees(
                math.atan2(current_pos.y() - center_pos.y(), current_pos.x() - center_pos.x())
                - math.atan2(
                    self.initial_rotation_pos.y() - center_pos.y(), self.initial_rotation_pos.x() - center_pos.x()
                )
            )
            self.setRotation(self.rotation() + angle)
            self.initial_rotation_pos = current_pos
            self.rotationChanged.emit(self.rotation())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.rotating = False
        self.resizing = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def setSelected(self, selected):
        super().setSelected(selected)
        if self.resize_enabled:
            self.resize_handle.setVisible(selected)
        if self.rotate_enabled:
            self.rotate_origin.setVisible(selected)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if self.resize_enabled:
                self.resize_handle.setVisible(value)
            if self.rotate_enabled:
                self.rotate_origin.setVisible(value)
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            rect = self.scene().sceneRect()
            left = abs(self.boundingRect().left())
            top = abs(self.boundingRect().top())
            right = abs(self.boundingRect().right())
            bottom = abs(self.boundingRect().bottom())
            # Keep the item inside the scene rect
            if value.x() - left < rect.left():
                value.setX(rect.left() + left)
            elif value.x() + right > rect.right():
                value.setX(rect.right() - right)
            if value.y() - top < rect.top():
                value.setY(rect.top() + top)
            elif value.y() + bottom > rect.bottom():
                value.setY(rect.bottom() - bottom)
            self.positionChanged.emit(value.x(), value.y())
            return value
        return super().itemChange(change, value)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
