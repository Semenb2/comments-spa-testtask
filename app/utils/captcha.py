import io
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.http import HttpResponse

WIDTH = 180
HEIGHT = 56
LENGTH = 5
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG_COLOR_TOP = (255, 255, 255)
BG_COLOR_BOTTOM = (230, 240, 255)
TEXT_COLOR = (30, 60, 180) 
LINE_COLOR = (160, 190, 255)
NOISE = 15  



def gen_code():
    chars = string.ascii_uppercase + "23456789"
    exclude = "0O1I"
    chars = ''.join([c for c in chars if c not in exclude])
    return ''.join(random.choice(chars) for _ in range(LENGTH))


def generate_captcha_image(code):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR_BOTTOM)
    draw = ImageDraw.Draw(image)

    for y in range(HEIGHT):
        r = BG_COLOR_TOP[0] + int((BG_COLOR_BOTTOM[0] - BG_COLOR_TOP[0]) * y / HEIGHT)
        g = BG_COLOR_TOP[1] + int((BG_COLOR_BOTTOM[1] - BG_COLOR_TOP[1]) * y / HEIGHT)
        b = BG_COLOR_TOP[2] + int((BG_COLOR_BOTTOM[2] - BG_COLOR_TOP[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    try:
        font = ImageFont.truetype(FONT_PATH, 32)
    except:
        font = ImageFont.load_default()

    spacing = WIDTH // (len(code) + 1)
    for i, char in enumerate(code):
        pos_x = 10 + i * spacing
        pos_y = random.randint(4, 10)
        angle = random.uniform(-12, 12)

        txt_img = Image.new("RGBA", (50, 50), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((5, 5), char, font=font, fill=TEXT_COLOR)
        txt_img = txt_img.rotate(angle, expand=1)
        image.paste(txt_img, (pos_x, pos_y), txt_img)

    for _ in range(2):
        start = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        end = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        draw.line([start, end], fill=LINE_COLOR, width=2)

    for _ in range(NOISE):
        draw.point((random.randint(0, WIDTH), random.randint(0, HEIGHT)), fill=(200, 200, 255))

    image = image.filter(ImageFilter.SMOOTH_MORE)

    return image


def captcha_image(code):
    img = generate_captcha_image(code)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")

