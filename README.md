# Python DICOM Converter

A simple tool to convert DICOM files into PNG and GIF images.

## Description

This program scans a directory for DICOM files and automatically converts them to images. 2D images are saved as PNG files, while 3D images (slice sequences) are exported as animated GIFs.

## Installation

Install the required dependencies with pip:

```bash
pip install pydicom pillow numpy
```

## Usage

Place your DICOM files in the `data/` folder then run:

```bash
python main.py
```

Generated images will be saved in the `output/` folder while preserving the source directory structure.

## Configuration

You can modify the parameters at the beginning of the `main.py` file:

```python
input_dicom_folder = "data"           # Source folder
output_folder = 'output'              # Destination folder
output_image_width = 480              # Image width
output_image_height = 480             # Image height
duration_in_milliseconds_between_each_image = 200  # GIF speed
```

## Output Format

2D images are converted to PNG. 3D images are converted to animated GIFs where each frame corresponds to a slice of the volumetric image. All images are normalized between 0 and 255 and resized according to the configured dimensions.