import json
from PIL import Image, ImageDraw, ImageFont


class ImageGen:
    def write_text_on_image(
        image_path,
        output_path,
        text,
        position,
        font_path=None,
        font_size=40,
        text_color="white",
    ):
        """
        Write text onto an image and save the result.

        :param image_path: Path to the input image.
        :param output_path: Path to save the output image.
        :param text: The text to write on the image.
        :param position: Tuple (x, y) specifying the position of the text.
        :param font_path: Path to the .ttf font file (optional).
        :param font_size: Font size for the text.
        :param text_color: Color of the text.
        """
        # Open the image
        image = ImageGen.open(image_path)

        # Create a drawing object
        draw = ImageDraw.Draw(image)

        # Load the font
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()

        # Write text on the image
        draw.text(position, text, fill=text_color, font=font)

        # Save the output image
        image.save(output_path)
        print(f"Text written on image and saved to {output_path}")

    image_path = r"d:\GIT\BLOOM\BLOOM\data\example_image.jpg"  # Input image path
    output_path = r"d:\GIT\BLOOM\BLOOM\data\output_image.jpg"  # Output image path
    text = "Hello, World!"  # Text to write
    position = (50, 50)  # Position (x, y) of the text
    font_path = (
        r"d:\GIT\BLOOM\BLOOM\fonts\OpenSans-ExtraBold.ttf"  # Path to the font file
    )
    font_size = 50  # Font size
    text_color = "white"  # Text color

    write_text_on_image(
        image_path, output_path, text, position, font_path, font_size, text_color
    )
