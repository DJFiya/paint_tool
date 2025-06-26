import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QColorDialog, QLabel, QGridLayout, QSpinBox
)
from PyQt6.QtGui import QColor, QPainter, QMouseEvent, QPen
from PyQt6.QtCore import Qt


class Pixel(QWidget):
    def __init__(self, x, y, size, color=Qt.GlobalColor.white):
        super().__init__()
        self.x = x
        self.y = y
        self.color = QColor(color)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Fill the pixel with its color
        painter.fillRect(self.rect(), self.color)

        # Draw a light gray grid line
        pen = QPen(QColor(200, 200, 200))  # Light gray
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def set_color(self, color: QColor):
        self.color = color
        self.update()


class PixelCanvas(QWidget):
    def __init__(self, grid_size=16, pixel_size=20):
        super().__init__()
        self.grid_size = grid_size
        self.pixel_size = pixel_size
        self.current_tool = "Pen"
        self.current_color = QColor(Qt.GlobalColor.black)
        self.start_pos = None
        self.setStyleSheet("background-color: #888888;")  # Gray canvas background
        self.init_grid()

    def init_grid(self):
        self.grid = [
            [Pixel(x, y, self.pixel_size) for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.layout.addWidget(self.grid[y][x], y, x)

        self.setLayout(self.layout)

    def set_tool(self, tool):
        self.current_tool = tool

    def set_color(self, color: QColor):
        self.current_color = color

    def mousePressEvent(self, event: QMouseEvent):
        widget = self.childAt(event.pos())
        if isinstance(widget, Pixel):
            x, y = widget.x, widget.y
            if self.current_tool == "Pen":
                self.grid[y][x].set_color(self.current_color)
            elif self.current_tool == "Fill":
                self.flood_fill(x, y, self.grid[y][x].color)
            elif self.current_tool == "Rect":
                self.start_pos = (x, y)

    def mouseReleaseEvent(self, event: QMouseEvent):
        widget = self.childAt(event.pos())
        if self.current_tool != "Rect" or not self.start_pos or not isinstance(widget, Pixel):
            return

        x_end, y_end = widget.x, widget.y
        x0, y0 = self.start_pos
        x1, y1 = min(x0, x_end), min(y0, y_end)
        x2, y2 = max(x0, x_end), max(y0, y_end)

        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.grid[y][x].set_color(self.current_color)

        self.start_pos = None

    def flood_fill(self, x, y, target_color):
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return
        if self.grid[y][x].color == self.current_color or self.grid[y][x].color != target_color:
            return

        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if 0 <= cx < self.grid_size and 0 <= cy < self.grid_size:
                pixel = self.grid[cy][cx]
                if pixel.color == target_color:
                    pixel.set_color(self.current_color)
                    stack.extend([
                        (cx + 1, cy), (cx - 1, cy),
                        (cx, cy + 1), (cx, cy - 1)
                    ])

    def resize_grid(self, new_size):
        old_colors = [
            [self.grid[y][x].color for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]

        self.grid_size = new_size

        # Clear layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            self.layout.removeWidget(widget)
            widget.deleteLater()

        # Create new grid
        self.grid = [
            [Pixel(x, y, self.pixel_size) for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Map old color if it exists
                old_x = int(x * len(old_colors[0]) / new_size)
                old_y = int(y * len(old_colors) / new_size)
                color = old_colors[old_y][old_x] if old_y < len(old_colors) and old_x < len(old_colors[0]) else QColor(Qt.GlobalColor.white)
                self.grid[y][x].set_color(color)
                self.layout.addWidget(self.grid[y][x], y, x)


class PixelPainter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Painter")
        self.canvas = PixelCanvas()

        self.tool_buttons = {
            "Pen": QPushButton("Pen"),
            "Fill": QPushButton("Fill"),
            "Rect": QPushButton("Rectangle"),
        }

        for name, btn in self.tool_buttons.items():
            btn.clicked.connect(lambda _, n=name: self.canvas.set_tool(n))

        self.color_button = QPushButton("Color")
        self.color_button.clicked.connect(self.select_color)

        self.resize_label = QLabel("Grid size:")
        self.resize_spinner = QSpinBox()
        self.resize_spinner.setRange(4, 64)
        self.resize_spinner.setValue(16)
        self.resize_spinner.valueChanged.connect(self.resize_grid)

        controls = QHBoxLayout()
        for btn in self.tool_buttons.values():
            controls.addWidget(btn)
        controls.addWidget(self.color_button)
        controls.addWidget(self.resize_label)
        controls.addWidget(self.resize_spinner)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.resize(500, 600)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_color(color)

    def resize_grid(self):
        new_size = self.resize_spinner.value()
        self.canvas.resize_grid(new_size)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    painter = PixelPainter()
    painter.show()
    sys.exit(app.exec())
