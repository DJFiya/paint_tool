# Pixel Painter

Pixel Painter is an enhanced pixel art drawing tool built with Python and PyQt6. It allows you to create pixel art using a grid-based canvas with a variety of drawing tools and features.

## Features

- **Pen Tool:** Draw individual pixels with the selected color.
- **Eraser Tool:** Erase pixels (set them to white).
- **Fill Tool:** Fill an area of connected pixels with the selected color (flood fill).
- **Rectangle Tool:** Draw filled rectangles by dragging from one pixel to another.
- **Circle Tool:** Draw filled circles by dragging from a center pixel.
- **Eyedropper Tool:** Pick a color from the canvas to use as the current color.
- **Color Picker:** Choose any color using a color dialog.
- **Color Palette:** Quickly select from a palette of common colors.
- **Resizable Grid:** Change the grid size (from 8x8 up to 64x64) while preserving your artwork as much as possible.
- **Show/Hide Grid:** Toggle grid lines on the canvas.
- **File Operations:** New, Save, Load, and Clear canvas options (save/load as JSON).
- **Modern UI:** Easy-to-use interface with grouped tool buttons, color controls, and settings.

## Requirements

- Python 3.7+
- PyQt6

Install PyQt6 with pip if you don't have it:

```bash
pip install PyQt6
```

## Usage

1. Run the application:

    ```bash
    python main.py
    ```

2. Use the tool buttons to select Pen, Eraser, Fill, Rectangle, Circle, or Eyedropper.
3. Click the color button or choose from the palette to set the drawing color.
4. Adjust the grid size using the spinner (Grid Size).
5. Toggle the grid lines with the "Show Grid" checkbox.
6. Use the file operations to create a new canvas, save your work, load a saved canvas, or clear the canvas.
7. Draw on the canvas by clicking or dragging as appropriate for the selected tool.

## File Structure

- `main.py` - Main application code.
- `README.md` - This file.
