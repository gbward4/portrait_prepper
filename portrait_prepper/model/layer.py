from PIL import Image

class Layer:

    def __init__(
            self, 
            name,
            raw_image,
            threshold_percent,
            canvas_color=(255, 255, 255),
            ):

        self.name = name
        self.canvas_color = canvas_color

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
