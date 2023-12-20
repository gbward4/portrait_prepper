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

def display_reference_image(self, image):
    pixmap = self.pil2pixmap(image)
    self.reference_image_label.setPixmap(pixmap)

def display_image(self, image):
    pixmap = self.pil2pixmap(image)
    self.image_label.setPixmap(pixmap)
    
def update_image(self):
    if not self.original_image:
        return

    shadow_layer = Layer(name="shadow", raw_image=self.original_image, threshold_percent=self.shadow_slider.slider.value(), canvas_color=(0, 0, 0))
    midtone_layer = Layer(name="midtone", raw_image=self.original_image, threshold_percent=self.midtone_slider.slider.value(), canvas_color=(0x58, 0x09, 0x9C))
    fleshtone_layer = Layer(name="fleshtone", raw_image=self.original_image, threshold_percent=self.fleshtone_slider.slider.value(), canvas_color=(0xFF, 0xAE, 0))

    composite_image = Image.new('RGBA', shadow_layer.size, (255, 255, 255, 255))
    composite_image = Image.composite(composite_image, fleshtone_layer.colored_canvas, fleshtone_layer.threshold_mask)
    composite_image = Image.composite(composite_image, midtone_layer.colored_canvas, midtone_layer.threshold_mask)
    composite_image = Image.composite(composite_image, shadow_layer.colored_canvas, shadow_layer.threshold_mask)

    self.composite_image = composite_image

    self.update_histogram()

    self.display_image(composite_image)