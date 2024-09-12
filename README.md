# Python EXIF Tool

![Cover Image](.assets/image.png)

Python EXIF Tool is a command-line utility and GUI application that allows you to group/rename images based on their EXIF data. It provides functionalities such as renaming images based on their EXIF DateTime and grouping images by location.

## Features

- Extract EXIF data including DateTime and GPS information from images.
- Rename images based on their EXIF DateTime.
- Group images by location using GPS coordinates.
- Calculate the approximate distance between two GPS coordinates.
- Support for various units of measurement for distance calculation.
- GUI application for easy and intuitive usage.

## Installation

1. Clone the repository.

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-Line Interface (CLI)

To use the command-line interface, navigate to the project directory and run the `exif_tool.py` script with the desired options.

```bash
python exif_tool.py [options]
```

Available options:

- `-h, --help`: Show the help message and exit.
- `-r, --recursive`: Process images recursively in subdirectories.
- `-d, --date-format`: Specify the date format for renaming images (default: "%Y-%m-%d\_%H-%M-%S").
- `-g, --group`: Group images by location using GPS coordinates.
- `-o, --output-folder`: Specify the output folder for processed images.

### Graphical User Interface (GUI)

To use the graphical user interface, run the `exif_tool_gui.py` script.

```bash
python exif_tool_gui.py
```

The GUI application will open, allowing you to browse and select the input and output folders, choose the desired function (rename or group), and configure additional options.

## Co-created with AI

This project was co-created with the assistance of GitHub Copilot and ChatGPT, AI programming assistants.

## Disclaimer

Use this project at your own risk. I am not responsible for any issues, damages, or unintended consequences that may arise from using this code. Always review the code and test it in your environment.

**Note**: This project is provided "as is" without any warranties.

## Credits

Cover Image by Mike Bird from Pexels: https://www.pexels.com/photo/eight-photo-frame-of-flowers-1100008/
