from PIL import Image, ImageFilter

def apply_threshold(image, threshold_value=128)
    grayscaled_img = image.convert("L")
    thresholded_img = grayscaled_img.point(lambda x: 0 if x < threshold_value else 255, '1')
    return threshold_img


input_image_path = "./input/input.jpg"
output_image_path = "./output/output.jpg"

raw_image = Image.open(input_image_path)
thresh_img = apply_threshold(raw_image)
thresh_img.save(output_image_path)

