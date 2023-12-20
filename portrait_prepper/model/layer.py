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
