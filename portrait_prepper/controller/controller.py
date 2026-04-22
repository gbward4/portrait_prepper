from importlib import resources
from PIL import Image, ImageOps
from portrait_prepper.model.composite_image import pil2pixmap
from portrait_prepper.model.layer import Layer
from portrait_prepper.model.histogram import get_histogram
from portrait_prepper.view.gui import SliderGroup
from copy import copy

colors = [(0, 0, 0), (0x58, 0x09, 0x9C), (0xFF, 0xAE, 0), (0, 0, 0), (0x58, 0x09, 0x9C), (0xFF, 0xAE, 0)]


class Layer():

    def __init__(self, color, stack_order):
        self.color = color
        self.stack_order = stack_order

class MainController():
    """ Main Controller Class """

    def __init__(self, view):
        self.view = view

        self.view.signals.image_reverse_state_changed.connect(self.update_images)
        self.view.signals.autocontrast_state_changed.connect(self.update_images)
        self.view.signals.composite_sliders_updated.connect(self.update_images)
        self.view.signals.save_image.connect(self.save_image)
        self.view.signals.load_image.connect(self.open_image)
        self.view.signals.update_layer_color.connect(self.update_layer_color)
        self.view.signals.delete_layer_request.connect(self.delete_layer)
        self.view.signals.add_layer_request.connect(self.user_requested_add_layer)

        self._original_image = None
        self.composite_image = None
        self.histogram = None

        self.shadow_color =(0, 0, 0)
        self.midtone_color = (0x58, 0x09, 0x9C)
        self.fleshtone_color = (0xFF, 0xAE, 0)

        self.layers = []

        self.build_sliders()  # todo move to setup

        self.default_image_path = resources.files("portrait_prepper.resources") / "ricky.jpg"
        # self.open_image(self.default_image_path)


    def build_sliders(self):
        default_num_layers = 3
        slider_spacing = int(100 / (default_num_layers + 1))
        for layer_idx in range(default_num_layers):
            default_slider_value = ((layer_idx + 1) * slider_spacing)
            self.add_layer(default_slider_value)

    # for idx in range(num_sliders_default):
    #     slider_group.slider.valueChanged.connect(lambda _, i=idx: self.update_composite_sliders(i))  # udpate to emit layer number
    #     slider_group.btn_palette.clicked.connect(lambda _, i=idx, c=color: self.change_layer_color_requested(i, c))
    #     slider_group.btn_trash.clicked.connect(lambda _, i=idx: self.delete_layer_requested(i))
    #     self.sliders.append(slider_group)

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

    def add_layer(self, default_slider_value=0):
        stack_order = len(self.layers)  # zero indexed
        layer = Layer(color=colors[stack_order], stack_order=stack_order)  # going to break on index error
        self.layers.append(layer)
        slider_group = SliderGroup(layer_identity=stack_order, value=default_slider_value)
        self.view.sliders_layout.addWidget(slider_group)

    def user_requested_add_layer(self):
        self.add_layer(4)

    def delete_layer(self):
        # pop layer
        # remove slider by name
        pass

    def update_layer_color(self, layer, color):
        pass
        # TODO STOPPED HERE.  GUI UPDATED, BUT CONTROLLER NEEDS UPDATE TO HANDLE LAYERS
        # self.update_images()

    def update_shadow_color(self, color):
        self.shadow_color = (color.red(), color.green(), color.blue())
        self.update_images()

    def update_midtone_color(self, color):
        self.midtone_color = (color.red(), color.green(), color.blue())
        self.update_images()

    def update_fleshtone_color(self, color):
        self.fleshtone_color = (color.red(), color.green(), color.blue())
        self.update_images()


    def setup(self):
        """ Some setup actions to do before opening Main Window """

    def save_image(self, file_path):
        self.composite_image.save(file_path)

    def open_image(self, file_path):
        image = Image.open(file_path)
        self._original_image = self.fix_exif_rotation(image)
        self.update_images()

    def fix_exif_rotation(self, image):
        # Check for and retrieve the orientation EXIF tag
        try:
            exif_orientation = image._getexif().get(274, 1)
        except (AttributeError, KeyError, IndexError):
            exif_orientation = 1  # Default orientation if not found

        # Rotate the image based on the EXIF orientation tag
        if exif_orientation == 3:
            image = image.rotate(180, expand=True)
        elif exif_orientation == 6:
            image = image.rotate(-90, expand=True)
        elif exif_orientation == 8:
            image = image.rotate(90, expand=True)

        return image


    def update_reference_image(self):
        pixmap = pil2pixmap(self.reference_image)
        self.view.signals.update_reference_image.emit(pixmap)

    def update_composite_image(self):
        self.build_composite_image()
        pixmap = pil2pixmap(self.composite_image)
        self.view.signals.update_composite_image.emit(pixmap)

    def build_composite_image(self):
        layers = []
        slider_groups = self.view.sliders
        for slider_group in slider_groups:
            # TODO I'm stuck here on shadow_color, should pick some gradient and move on for now.  In future it should have presets, and slider group should have a color identity
            # TODO make a "layer" object that has "identity, color, threshold" attrs, 
            # TODO make three color groups, shadow midtone, fleshtone that have a default color.  What I really want to do is divide in three groups and then show divisions there
            layer = Layer(name="", raw_image=self.reference_image, threshold_percent=slider_group.slider.slider_value(), canvas_color=self.shadow_color)
            layers.append(layer)

        shadow_layer = Layer(name="shadow", raw_image=self.reference_image, threshold_percent=self.view.shadow_slider.slider.slider_value(), canvas_color=self.shadow_color)
        midtone_layer = Layer(name="midtone", raw_image=self.reference_image, threshold_percent=self.view.midtone_slider.slider.slider_value(), canvas_color=self.midtone_color)
        fleshtone_layer = Layer(name="fleshtone", raw_image=self.reference_image, threshold_percent=self.view.fleshtone_slider.slider.slider_value(), canvas_color=self.fleshtone_color)

        composite_image = Image.new('RGBA', shadow_layer.size, (255, 255, 255, 255))
        composite_image = Image.composite(composite_image, fleshtone_layer.colored_canvas, fleshtone_layer.threshold_mask)
        composite_image = Image.composite(composite_image, midtone_layer.colored_canvas, midtone_layer.threshold_mask)
        composite_image = Image.composite(composite_image, shadow_layer.colored_canvas, shadow_layer.threshold_mask)

        self.composite_image = composite_image

    def update_histogram(self):
        threshold_lines = [
            self.view.shadow_slider.slider.slider_value(),
            self.view.midtone_slider.slider.slider_value(),
            self.view.fleshtone_slider.slider.slider_value(),
        ]
        self.histogram = get_histogram(self.reference_image, threshold_lines)

        pixmap = pil2pixmap(self.histogram)
        self.view.signals.update_histogram.emit(pixmap)

