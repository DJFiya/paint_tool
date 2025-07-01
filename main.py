import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QColorDialog, QLabel, QGridLayout, QSpinBox,
    QFileDialog, QMessageBox, QFrame, QButtonGroup, QToolButton,
    QGroupBox, QSlider, QCheckBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import (
    QColor, QPainter, QMouseEvent, QPen, QIcon, QPixmap, 
    QFont, QPalette, QBrush
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal


class ColorButton(QPushButton):
    """Custom color button that displays the current color"""
    def __init__(self, color=Qt.GlobalColor.black, size=30):
        super().__init__()
        self.color = QColor(color)
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 2px solid #333;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #555;
            }}
            QPushButton:pressed {{
                border: 2px solid #777;
            }}
        """)

    def set_color(self, color):
        self.color = QColor(color)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 2px solid #333;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #555;
            }}
            QPushButton:pressed {{
                border: 2px solid #777;
            }}
        """)


class Pixel(QWidget):
    def __init__(self, x, y, size, color=Qt.GlobalColor.white):
        super().__init__()
        self.x = x
        self.y = y
        self.color = QColor(color)
        self.setFixedSize(size, size)
        self.show_grid = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Fill the pixel with its color
        painter.fillRect(self.rect(), self.color)

        # Draw grid lines if enabled
        if self.show_grid:
            pen = QPen(QColor(180, 180, 180))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def set_color(self, color: QColor):
        self.color = color
        self.update()

    def set_grid_visible(self, visible):
        self.show_grid = visible
        self.update()


class PixelCanvas(QWidget):
    colorPicked = pyqtSignal(QColor)
    
    def __init__(self, grid_size=16, pixel_size=20):
        super().__init__()
        self.grid_size = grid_size
        self.pixel_size = pixel_size
        self.current_tool = "Pen"
        self.current_color = QColor(Qt.GlobalColor.black)
        self.start_pos = None
        self.is_drawing = False
        self.show_grid = True
        
        # Style the canvas
        self.setStyleSheet("""
            PixelCanvas {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
        """)
        
        self.init_grid()

    def init_grid(self):
        self.grid = [
            [Pixel(x, y, self.pixel_size) for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 10, 10, 10)

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.layout.addWidget(self.grid[y][x], y, x)

        self.setLayout(self.layout)

    def set_tool(self, tool):
        self.current_tool = tool

    def set_color(self, color: QColor):
        self.current_color = color

    def set_grid_visible(self, visible):
        self.show_grid = visible
        for row in self.grid:
            for pixel in row:
                pixel.set_grid_visible(visible)

    def mousePressEvent(self, event: QMouseEvent):
        widget = self.childAt(event.pos())
        if isinstance(widget, Pixel):
            self.is_drawing = True
            x, y = widget.x, widget.y
            
            if self.current_tool == "Pen":
                self.grid[y][x].set_color(self.current_color)
            elif self.current_tool == "Eraser":
                self.grid[y][x].set_color(QColor(Qt.GlobalColor.white))
            elif self.current_tool == "Eyedropper":
                picked_color = self.grid[y][x].color
                self.colorPicked.emit(picked_color)
            elif self.current_tool == "Fill":
                self.flood_fill(x, y, self.grid[y][x].color)
            elif self.current_tool == "Rectangle":
                self.start_pos = (x, y)
            elif self.current_tool == "Circle":
                self.start_pos = (x, y)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.is_drawing:
            return
            
        widget = self.childAt(event.pos())
        if isinstance(widget, Pixel):
            x, y = widget.x, widget.y
            
            if self.current_tool == "Pen":
                self.grid[y][x].set_color(self.current_color)
            elif self.current_tool == "Eraser":
                self.grid[y][x].set_color(QColor(Qt.GlobalColor.white))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_drawing = False
        widget = self.childAt(event.pos())
        
        if self.current_tool == "Rectangle" and self.start_pos and isinstance(widget, Pixel):
            x_end, y_end = widget.x, widget.y
            self.draw_rectangle(self.start_pos, (x_end, y_end))
            self.start_pos = None
        elif self.current_tool == "Circle" and self.start_pos and isinstance(widget, Pixel):
            x_end, y_end = widget.x, widget.y
            self.draw_circle(self.start_pos, (x_end, y_end))
            self.start_pos = None

    def draw_rectangle(self, start, end):
        x0, y0 = start
        x_end, y_end = end
        x1, y1 = min(x0, x_end), min(y0, y_end)
        x2, y2 = max(x0, x_end), max(y0, y_end)

        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    self.grid[y][x].set_color(self.current_color)

    def draw_circle(self, start, end):
        x0, y0 = start
        x1, y1 = end
        
        # Calculate radius
        radius = max(abs(x1 - x0), abs(y1 - y0))
        
        # Draw circle using midpoint circle algorithm (simplified)
        for y in range(max(0, y0 - radius), min(self.grid_size, y0 + radius + 1)):
            for x in range(max(0, x0 - radius), min(self.grid_size, x0 + radius + 1)):
                dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
                if dist <= radius:
                    self.grid[y][x].set_color(self.current_color)

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

    def clear_canvas(self):
        for row in self.grid:
            for pixel in row:
                pixel.set_color(QColor(Qt.GlobalColor.white))

    def resize_grid(self, new_size):
        # Store current colors
        old_colors = [
            [self.grid[y][x].color for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]

        self.grid_size = new_size

        # Clear layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                self.layout.removeWidget(widget)
                widget.deleteLater()

        # Create new grid
        self.grid = [
            [Pixel(x, y, self.pixel_size) for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Scale old content to new size
                if old_colors:
                    old_x = min(int(x * len(old_colors[0]) / new_size), len(old_colors[0]) - 1)
                    old_y = min(int(y * len(old_colors) / new_size), len(old_colors) - 1)
                    color = old_colors[old_y][old_x]
                else:
                    color = QColor(Qt.GlobalColor.white)
                
                self.grid[y][x].set_color(color)
                self.grid[y][x].set_grid_visible(self.show_grid)
                self.layout.addWidget(self.grid[y][x], y, x)

    def get_canvas_data(self):
        """Export canvas as color data"""
        return [
            [self.grid[y][x].color.name() for x in range(self.grid_size)]
            for y in range(self.grid_size)
        ]

    def load_canvas_data(self, data):
        """Load canvas from color data"""
        if not data:
            return
            
        new_size = len(data)
        if new_size != self.grid_size:
            self.resize_grid(new_size)
        
        for y in range(min(len(data), self.grid_size)):
            for x in range(min(len(data[y]), self.grid_size)):
                color = QColor(data[y][x])
                self.grid[y][x].set_color(color)


class PixelPainter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Pixel Painter")
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 2px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #999;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #4a90e2;
                color: white;
                border-color: #357abd;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        self.canvas = PixelCanvas()
        self.canvas.colorPicked.connect(self.on_color_picked)
        
        self.setup_ui()
        self.setup_tool_group()
        
        # Set default tool
        self.tool_buttons["Pen"].setChecked(True)

    def setup_ui(self):
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel for tools and controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout()
        
        self.tool_buttons = {}
        tools = [
            ("Pen", "✏️"),
            ("Eraser", "🧽"),
            ("Fill", "🪣"),
            ("Rectangle", "⬜"),
            ("Circle", "⭕"),
            ("Eyedropper", "💧")
        ]
        
        for tool_name, icon in tools:
            btn = QPushButton(f"{icon} {tool_name}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=tool_name: self.set_tool(name))
            self.tool_buttons[tool_name] = btn
            tools_layout.addWidget(btn)
        
        tools_group.setLayout(tools_layout)
        left_panel.addWidget(tools_group)
        
        # Colors group
        colors_group = QGroupBox("Colors")
        colors_layout = QVBoxLayout()
        
        # Current color display
        color_display_layout = QHBoxLayout()
        color_display_layout.addWidget(QLabel("Current:"))
        self.current_color_btn = ColorButton(Qt.GlobalColor.black, 40)
        self.current_color_btn.clicked.connect(self.select_color)
        color_display_layout.addWidget(self.current_color_btn)
        color_display_layout.addStretch()
        colors_layout.addLayout(color_display_layout)
        
        # Color palette
        palette_layout = QGridLayout()
        self.palette_colors = [
            Qt.GlobalColor.black, Qt.GlobalColor.white, Qt.GlobalColor.red, Qt.GlobalColor.green,
            Qt.GlobalColor.blue, Qt.GlobalColor.yellow, Qt.GlobalColor.magenta, Qt.GlobalColor.cyan,
            Qt.GlobalColor.darkRed, Qt.GlobalColor.darkGreen, Qt.GlobalColor.darkBlue, Qt.GlobalColor.darkYellow,
            Qt.GlobalColor.darkMagenta, Qt.GlobalColor.darkCyan, Qt.GlobalColor.gray, Qt.GlobalColor.darkGray
        ]
        
        for i, color in enumerate(self.palette_colors):
            btn = ColorButton(color, 25)
            btn.clicked.connect(lambda checked, c=color: self.set_color(QColor(c)))
            palette_layout.addWidget(btn, i // 4, i % 4)
        
        colors_layout.addLayout(palette_layout)
        colors_group.setLayout(colors_layout)
        left_panel.addWidget(colors_group)
        
        # Canvas settings group
        settings_group = QGroupBox("Canvas Settings")
        settings_layout = QVBoxLayout()
        
        # Grid size
        grid_layout = QHBoxLayout()
        grid_layout.addWidget(QLabel("Grid Size:"))
        self.size_spinner = QSpinBox()
        self.size_spinner.setRange(8, 64)
        self.size_spinner.setValue(16)
        self.size_spinner.valueChanged.connect(self.resize_canvas)
        grid_layout.addWidget(self.size_spinner)
        settings_layout.addLayout(grid_layout)
        
        # Show grid checkbox
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.toggled.connect(self.toggle_grid)
        settings_layout.addWidget(self.grid_checkbox)
        
        settings_group.setLayout(settings_layout)
        left_panel.addWidget(settings_group)
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        file_buttons = [
            ("📁 New", self.new_canvas),
            ("💾 Save", self.save_canvas),
            ("📂 Load", self.load_canvas),
            ("🗑️ Clear", self.clear_canvas)
        ]
        
        for text, callback in file_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            file_layout.addWidget(btn)
        
        file_group.setLayout(file_layout)
        left_panel.addWidget(file_group)
        
        # Add stretch to push everything to top
        left_panel.addStretch()
        
        # Add panels to main layout
        main_layout.addLayout(left_panel)
        main_layout.addWidget(self.canvas, 1)
        
        self.setLayout(main_layout)
        self.resize(800, 600)

    def setup_tool_group(self):
        """Setup button group for tools to ensure only one is selected"""
        self.tool_group = QButtonGroup()
        for btn in self.tool_buttons.values():
            self.tool_group.addButton(btn)

    def set_tool(self, tool_name):
        self.canvas.set_tool(tool_name)

    def set_color(self, color):
        self.canvas.set_color(color)
        self.current_color_btn.set_color(color)

    def on_color_picked(self, color):
        """Handle color picked from eyedropper tool"""
        self.set_color(color)

    def select_color(self):
        color = QColorDialog.getColor(self.canvas.current_color, self, "Select Color")
        if color.isValid():
            self.set_color(color)

    def resize_canvas(self):
        new_size = self.size_spinner.value()
        self.canvas.resize_grid(new_size)

    def toggle_grid(self, checked):
        self.canvas.set_grid_visible(checked)

    def new_canvas(self):
        reply = QMessageBox.question(
            self, "New Canvas", 
            "Create a new canvas? This will clear your current work.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_canvas()

    def clear_canvas(self):
        self.canvas.clear_canvas()

    def save_canvas(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Canvas", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                data = {
                    "grid_size": self.canvas.grid_size,
                    "colors": self.canvas.get_canvas_data()
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                QMessageBox.information(self, "Success", "Canvas saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save canvas:\n{str(e)}")

    def load_canvas(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Canvas", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                if "colors" in data:
                    self.canvas.load_canvas_data(data["colors"])
                    if "grid_size" in data:
                        self.size_spinner.setValue(data["grid_size"])
                    QMessageBox.information(self, "Success", "Canvas loaded successfully!")
                else:
                    QMessageBox.warning(self, "Invalid File", "This file doesn't contain valid canvas data.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load canvas:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern looking style
    
    painter = PixelPainter()
    painter.show()
    
    sys.exit(app.exec())