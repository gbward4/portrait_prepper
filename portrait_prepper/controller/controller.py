from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PIL import Image, ImageOps
from portrait_prepper.model.composite_image import pil2pixmap
from portrait_prepper.model.layer import Layer
from portrait_prepper.model.histogram import get_histogram
from copy import copy


class MainController():
    """ Main Controller Class """

    def __init__(self, view):
        self.view = view

        self.view.signals.image_reverse_state_changed.connect(self.update_images)
        self.view.signals.autocontrast_state_changed.connect(self.update_images)
        self.view.signals.composite_sliders_updated.connect(self.update_images)
        self.view.signals.save_image.connect(self.save_image)
        self.view.signals.load_image.connect(self.open_image)

        self._original_image = None
        self.composite_image = None
        self.histogram = None

    @property
    def reference_image(self):
        img = copy(self._original_image)
        if self.view.checkbox_autocontrast.isChecked():
            img = self.autocontrasted_image(img)
        if self.view.checkbox_img_reverse.isChecked():
            img = self.reversed_image(img)

        return img

    def autocontrasted_image(self, image):
        return ImageOps.autocontrast(image, 1)

    def reversed_image(self, image):
        return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    def update_images(self):
        self.update_reference_image()
        self.update_composite_image()
        self.update_histogram()

    def setup(self):
        """ Some setup actions to do before opening Main Window """

    def save_image(self, file_path):
        self.composite_image.save(file_path)

    def open_image(self, file_path):
        self._original_image = Image.open(file_path)
        self.update_images()

    def update_reference_image(self):
        pixmap = pil2pixmap(self.reference_image)
        self.view.signals.update_reference_image.emit(pixmap)

    def update_composite_image(self):
        self.build_composite_image()
        pixmap = pil2pixmap(self.composite_image)
        self.view.signals.update_composite_image.emit(pixmap)

    def build_composite_image(self):
        shadow_layer = Layer(name="shadow", raw_image=self.reference_image, threshold_percent=self.view.shadow_slider.slider.value(), canvas_color=(0, 0, 0))
        midtone_layer = Layer(name="midtone", raw_image=self.reference_image, threshold_percent=self.view.midtone_slider.slider.value(), canvas_color=(0x58, 0x09, 0x9C))
        fleshtone_layer = Layer(name="fleshtone", raw_image=self.reference_image, threshold_percent=self.view.fleshtone_slider.slider.value(), canvas_color=(0xFF, 0xAE, 0))

        composite_image = Image.new('RGBA', shadow_layer.size, (255, 255, 255, 255))
        composite_image = Image.composite(composite_image, fleshtone_layer.colored_canvas, fleshtone_layer.threshold_mask)
        composite_image = Image.composite(composite_image, midtone_layer.colored_canvas, midtone_layer.threshold_mask)
        composite_image = Image.composite(composite_image, shadow_layer.colored_canvas, shadow_layer.threshold_mask)

        self.composite_image = composite_image

    def update_histogram(self):
        threshold_lines = [
            self.view.shadow_slider.slider.value(),
            self.view.midtone_slider.slider.value(),
            self.view.fleshtone_slider.slider.value(),
        ]
        self.histogram = get_histogram(self.reference_image, threshold_lines)

        pixmap = pil2pixmap(self.histogram)
        self.view.signals.update_histogram.emit(pixmap)

