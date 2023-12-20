from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageOps
import os


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

input_image_path = "./input/input.jpg"
output_image_dir = "./output/"
output_image_suffix = ".jpg"
threshold_lines = [25, 50, 75, 85]
rotate = False

raw_image = Image.open(input_image_path)
raw_image = raw_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
if rotate:
    raw_image = raw_image.transpose(Image.Transpose.ROTATE_270)
raw_image = raw_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
raw_image = ImageOps.autocontrast(raw_image, 0.0)
dump_histogram(raw_image, "./output/histogram.jpg", threshold_lines)

posterized_img = raw_image.quantize(colors=6)
posterized_img = posterized_img.convert("RGB")

enhancer = ImageEnhance.Contrast(raw_image)
darker_img = enhancer.enhance(1.5)
low_contrast_img = enhancer.enhance(0.5)

shadow_layer = Layer(name="shadow", raw_image=raw_image, threshold_percent=25, canvas_color=(0, 0, 0))
midtone_layer = Layer(name="midtone", raw_image=raw_image, threshold_percent=50, canvas_color=(0x58, 0x09, 0x9C))
fleshtone_layer = Layer(name="fleshtone", raw_image=raw_image, threshold_percent=75, canvas_color=(0xFF, 0xAE, 0))

shadow_layer.save_threshold_mask()
midtone_layer.save_threshold_mask()
fleshtone_layer.save_threshold_mask()

raw_image.save(os.path.join(output_image_dir, "orig_mirrored" + output_image_suffix))
posterized_img.save(os.path.join(output_image_dir, "posterized" + output_image_suffix))
darker_img.save(os.path.join(output_image_dir, "contrast_high" + output_image_suffix))
low_contrast_img.save(os.path.join(output_image_dir, "contrast_low" + output_image_suffix))

composite_image = Image.new('RGBA', shadow_layer.size, (255, 255, 255, 255))
composite_image = Image.composite(composite_image, fleshtone_layer.colored_canvas, fleshtone_layer.threshold_mask)
composite_image = Image.composite(composite_image, midtone_layer.colored_canvas, midtone_layer.threshold_mask)
composite_image = Image.composite(composite_image, shadow_layer.colored_canvas, shadow_layer.threshold_mask)
composite_image.save("./output/composite.png")

