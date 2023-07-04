from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import string
import os
from config import ROOT_PATH


def generate_captcha():
    width, height = 220, 100

    image = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    font_path = os.path.join(ROOT_PATH, 'fonts', 'A.ttf')
    font = ImageFont.truetype(font_path, size=50)

    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    x = 10
    y = 10

    for i, char in enumerate(captcha_text):
        char_width, char_height = (50, 50)
        char_x = x + i * char_width
        char_y = y
        angle = random.randint(-30, 30)
        char_image = Image.new('RGBA', (char_width, char_height), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((0, 0), char, font=font, fill=(200, 200, 0))
        char_image = char_image.rotate(angle, expand=1)
        image.paste(char_image, (char_x, char_y))

    for i in range(50):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(255, 255, 255))

    # сохраняем изображение капчи в буфер в памяти
    image_buffer = BytesIO()
    image.save(image_buffer, format='png')
    image_buffer.seek(0)

    return captcha_text, image_buffer
