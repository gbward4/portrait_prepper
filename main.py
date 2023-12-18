from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageOps
import os

def percent_to_8bit(percent):
    return (percent * 255) / 100

def apply_threshold(image, threshold_percent=50):
    """ Returns a thresholded image

    :param Image image: a PIL image object
    :param int threshold_percent: 0 to 100 percent
    """
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

shadow_img = apply_threshold(raw_image, threshold_lines[0])
midtone_img = apply_threshold(raw_image, threshold_lines[1])
fleshtone_img = apply_threshold(raw_image, threshold_lines[2])
highlights_img = apply_threshold(raw_image, threshold_lines[3])

shadow_img.save(os.path.join(output_image_dir, "shadow" + output_image_suffix))
midtone_img.save(os.path.join(output_image_dir, "midtone" + output_image_suffix))
fleshtone_img.save(os.path.join(output_image_dir, "fleshtone" + output_image_suffix))
highlights_img.save(os.path.join(output_image_dir, "highlights" + output_image_suffix))
raw_image.save(os.path.join(output_image_dir, "orig_mirrored" + output_image_suffix))
posterized_img.save(os.path.join(output_image_dir, "posterized" + output_image_suffix))
darker_img.save(os.path.join(output_image_dir, "contrast_high" + output_image_suffix))
low_contrast_img.save(os.path.join(output_image_dir, "contrast_low" + output_image_suffix))

images_to_composite = [highlights_img, fleshtone_img, midtone_img, shadow_img]

composite_image = Image.new('RGBA', shadow_img.size, (255, 255, 255, 255))

## Stack the thresholded images with varying saturation levels
for i, thresholded_image in enumerate(images_to_composite):
    alpha_channel = thresholded_image.point(lambda x: 0 if x > 0 else 255, 'L')
    thresholded_image = thresholded_image.convert("RGBA")
    thresholded_image.putalpha(alpha_channel)
    saturation_level = i / (len(images_to_composite) - 1)  # Vary saturation from 0 to 1
    blended_image = Image.blend(composite_image, thresholded_image, saturation_level)
    composite_image.paste(blended_image, (0, 0), blended_image)

# Save the composite image
composite_image.save("./output/composite.png")

# Can I blue, yellow it?


