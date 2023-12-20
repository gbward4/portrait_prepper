import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageOps, ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QWidget, QAction, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtRemoveInputHook


def apply_threshold(image, threshold_percent=50):
    """ Returns a thresholded image

    :param Image image: a PIL image object
    :param int threshold_percent: 0 to 100 percent
    """

    def percent_to_8bit(percent):
        """ Scale the percent into an 8 bit value """
        return int((percent * 255) / 100)

    threshold_value = percent_to_8bit(threshold_percent)

    grayscaled_img = image.convert("L")
    threshold_img = grayscaled_img.point(lambda x: 0 if x < threshold_value else 255, '1')

    return threshold_img

def get_histogram(image, threshold_lines):

    grayscale_image = image.convert("L")
    histogram = grayscale_image.histogram()

    # Create a new image for the histogram
    histogram_image = Image.new('RGB', (256, 100), color='white')
    draw = ImageDraw.Draw(histogram_image)

    # Draw the histogram
    for i in range(256):
        draw.line([(i, 100), (i, 100 - histogram[i] // 100)], fill='black')

    # Draw the threshold lines
    for th_line in threshold_lines:
        x = int(th_line * 256 / 100)
        draw.line([(x, 0), (x, 100)], fill='red')

    return histogram_image

def dump_histogram(image, output_path, threshold_lines):
    grayscale_image = image.convert("L")
    histogram = grayscale_image.histogram()

    # Create a new image for the histogram
    histogram_image = Image.new('RGB', (256, 100), color='white')
    draw = ImageDraw.Draw(histogram_image)

    # Draw the histogram
    for i in range(256):
        draw.line([(i, 100), (i, 100 - histogram[i] // 100)], fill='black')

    # Draw the threshold lines
    for th_line in threshold_lines:
        x = int(th_line * 256 / 100)
        draw.line([(x, 0), (x, 100)], fill='red')

    # Save the histogram image
    histogram_image.save(output_path)    

class Layer:

    def __init__(
            self, 
            name,
            raw_image,
            threshold_percent,
            canvas_color=(255, 255, 255),
            out_dir="./output",
            ):

        self.name = name
        self.out_dir = out_dir
        self.canvas_color=canvas_color

        self.threshold_percent = threshold_percent

        self._image = raw_image

    def save_threshold_mask(self):
        self.threshold_mask.save(os.path.join(self.out_dir, self.name + ".jpg"))

    @property
    def raw_image(self):
        return self._image

    @property
    def size(self):
        return self.raw_image.size

    @property
    def colored_canvas(self):
        R, G, B = self.canvas_color
        return Image.new("RGBA", self.raw_image.size, (R, G, B, 255))

    @property
    def threshold_mask(self):
        return apply_threshold(self.raw_image, self.threshold_percent)



class PictureEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Image Display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Original Image Display
        self.orig_image_label = QLabel(self)
        self.orig_image_label.setAlignment(Qt.AlignCenter)

        # Histogram Display
        self.histogram_label = QLabel(self)
        self.histogram_label.setAlignment(Qt.AlignCenter)

        # Sliders
        self.shadow_slider = QSlider(Qt.Horizontal)
        self.shadow_slider.setRange(0, 100)
        self.shadow_slider.setValue(25)
        self.shadow_slider.valueChanged.connect(self.update_image)

        self.midtone_slider = QSlider(Qt.Horizontal)
        self.midtone_slider.setRange(0, 100)
        self.midtone_slider.setValue(50)
        self.midtone_slider.valueChanged.connect(self.update_image)

        self.fleshtone_slider = QSlider(Qt.Horizontal)
        self.fleshtone_slider.setRange(0, 100)
        self.fleshtone_slider.setValue(75)
        self.fleshtone_slider.valueChanged.connect(self.update_image)

        # Layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        labels_layout = QHBoxLayout()
        labels_layout.addWidget(self.image_label)
        labels_layout.addWidget(self.orig_image_label)
        labels_layout.addWidget(self.histogram_label)

        sliders_layout = QVBoxLayout()
        sliders_layout.addWidget(self.shadow_slider)
        sliders_layout.addWidget(self.midtone_slider)
        sliders_layout.addWidget(self.fleshtone_slider)

        main_layout.addLayout(labels_layout)
        main_layout.addLayout(sliders_layout)

        self.setCentralWidget(central_widget)

        self.original_image = None

        self.setWindowTitle('Picture Editor')
        self.setGeometry(100, 100, 800, 600)

    def open_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)')

        if file_path:
            self.original_image = Image.open(file_path)
            # TODO Hack
            self.original_image = self.original_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.original_image = ImageOps.autocontrast(self.original_image, 0.0)

            self.display_image(self.original_image)
            self.display_orig_image(self.original_image)

    def save_image(self):
        # Todo handle no image
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Image', 'composite', 'Image Files (*.png)')

        self.composite_image.save(file_path)

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Histogram', 'histogram', 'Image Files (*.png)')
        self.histogram.save(file_path)

    def pil2pixmap(self, im):
        if im.mode == "RGB":
            r, g, b = im.split()
            im = Image.merge("RGB", (b, g, r))
        elif  im.mode == "RGBA":
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
        elif im.mode == "L":
            im = im.convert("RGBA")
        # Bild in RGBA konvertieren, falls nicht bereits passiert
        im2 = im.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap       

    def display_orig_image(self, image):
        pixmap = self.pil2pixmap(image)
        self.orig_image_label.setPixmap(pixmap)

    def display_image(self, image):
        pixmap = self.pil2pixmap(image)
        self.image_label.setPixmap(pixmap)

    def display_histogram(self, image):
        pixmap = self.pil2pixmap(image)
        self.histogram_label.setPixmap(pixmap)

    def update_histogram(self):
        threshold_lines = [
                self.shadow_slider.value(),
                self.midtone_slider.value(),
                self.fleshtone_slider.value(),
                ]

        self.histogram = get_histogram(self.original_image, threshold_lines)
        self.display_histogram(self.histogram)


    def update_image(self):
        if not self.original_image:
            return

        shadow_layer = Layer(name="shadow", raw_image=self.original_image, threshold_percent=self.shadow_slider.value(), canvas_color=(0, 0, 0))
        midtone_layer = Layer(name="midtone", raw_image=self.original_image, threshold_percent=self.midtone_slider.value(), canvas_color=(0x58, 0x09, 0x9C))
        fleshtone_layer = Layer(name="fleshtone", raw_image=self.original_image, threshold_percent=self.fleshtone_slider.value(), canvas_color=(0xFF, 0xAE, 0))

        composite_image = Image.new('RGBA', shadow_layer.size, (255, 255, 255, 255))
        composite_image = Image.composite(composite_image, fleshtone_layer.colored_canvas, fleshtone_layer.threshold_mask)
        composite_image = Image.composite(composite_image, midtone_layer.colored_canvas, midtone_layer.threshold_mask)
        composite_image = Image.composite(composite_image, shadow_layer.colored_canvas, shadow_layer.threshold_mask)

        self.composite_image = composite_image

        self.update_histogram()

        self.display_image(composite_image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = PictureEditor()
    editor.show()
    sys.exit(app.exec_())
