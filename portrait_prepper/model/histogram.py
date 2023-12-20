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
    
def display_histogram(self, image):
    pixmap = self.pil2pixmap(image)
    self.histogram_label.setPixmap(pixmap)

def update_histogram(self):
    threshold_lines = [
            self.shadow_slider.slider.value(),
            self.midtone_slider.slider.value(),
            self.fleshtone_slider.slider.value(),
            ]

    self.histogram = get_histogram(self.original_image, threshold_lines)
    self.display_histogram(self.histogram)