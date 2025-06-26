# Pixel Painter

Pixel Painter is a simple pixel art drawing tool built with Python and PyQt6. It allows you to create pixel art using a grid-based canvas with basic drawing tools.

## Features

- **Pen Tool:** Draw individual pixels with the selected color.
- **Fill Tool:** Fill an area of connected pixels with the selected color (flood fill).
- **Rectangle Tool:** Draw filled rectangles by dragging from one pixel to another.
- **Color Picker:** Choose any color using a color dialog.
- **Resizable Grid:** Change the grid size (from 4x4 up to 64x64) while preserving your artwork as much as possible.
- **Simple UI:** Easy-to-use interface with tool buttons and controls.

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

2. Use the tool buttons to select the Pen, Fill, or Rectangle tool.
3. Click the "Color" button to choose a drawing color.
4. Adjust the grid size using the spinner (Grid size).
5. Draw on the canvas by clicking or dragging as appropriate for the selected tool.

## File Structure

- `main.py` - Main application code.
- `README.md` - This file.

## License

This project is provided for educational purposes.
