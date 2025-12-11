# Copyright 2025 Tanvir Saklan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_email(
    subject: str,
    to: list[str],
    context: dict = None,
    template_name: str | None = None,
    body: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
    html: bool = True,
    from_email: str | None = None,
) -> bool:
    """
    Sends an email using Django's EmailMessage with optional HTML, CC, BCC, and attachments.
    """
    try:
        # Prepare body
        if template_name:
            message_body = render_to_string(template_name, context or {})
        elif body:
            message_body = body
        else:
            raise ValueError("Either template_name or body must be provided")

        # Create EmailMessage
        email = EmailMessage(
            subject=subject,
            body=message_body,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=to,
            cc=cc or [],
            bcc=bcc or [],
        )

        # HTML support
        if html:
            email.content_subtype = "html"

        # Attachments
        if attachments:
            for file_path in attachments:
                try:
                    email.attach_file(file_path)
                except Exception as e:
                    print(f"Attachment error for {file_path}: {e}")

        email.send(fail_silently=False)
        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False
    
import random
import string
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_captcha():
    # Random text (6 characters)
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    width, height = 200, 80
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Background gradient
    for y in range(height):
        r = 200 + random.randint(-20, 20)
        g = 200 + random.randint(-20, 20)
        b = 200 + random.randint(-20, 20)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Load multiple fonts (you can add more paths)
    fonts = [
        "/home/uch/mse/captcha_fonts/DejaVuSans-Bold.ttf",
        "/home/uch/mse/captcha_fonts/LiberationSerif-Bold.ttf",
        "/home/uch/mse/captcha_fonts/FreeSansBold.ttf"
    ]
    font = ImageFont.truetype(random.choice(fonts), 42)

    # Draw rotated characters
    char_images = []
    for char in text:
        char_img = Image.new('RGBA', (50, 60), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((5, 5), char, font=font,
                       fill=(random.randint(0, 120),
                             random.randint(0, 120),
                             random.randint(0, 120)))
        rotated = char_img.rotate(random.randint(-35, 35), expand=1)
        char_images.append(rotated)

    # Paste characters onto the main image with random spacing
    x_offset = 10
    for char_img in char_images:
        image.paste(char_img, (x_offset, random.randint(5, 20)), char_img)
        x_offset += random.randint(25, 35)

    draw = ImageDraw.Draw(image)

    # Add random curved lines
    for _ in range(3):
        points = [
            (random.randint(0, width), random.randint(0, height))
            for _ in range(4)
        ]
        draw.line(points, fill=(random.randint(50, 150),
                                random.randint(50, 150),
                                random.randint(50, 150)), width=2)

    # Add strong noise (dots)
    for _ in range(600):
        draw.point((random.randint(0, width), random.randint(0, height)),
                   fill=(random.randint(0, 255),
                         random.randint(0, 255),
                         random.randint(0, 255)))

    # Apply wave distortion
    def wave_distort(img):
        amplitude = random.randint(3, 6)
        wavelength = random.randint(30, 60)
        offset = random.randint(0, 360)
        new_img = Image.new("RGB", img.size, (255, 255, 255))
        for y in range(img.height):
            shift = int(amplitude * math.sin(2 * math.pi * y / wavelength + offset))
            for x in range(img.width):
                new_x = (x + shift) % img.width
                new_img.putpixel((x, y), img.getpixel((new_x, y)))
        return new_img

    image = wave_distort(image)
    image = image.filter(ImageFilter.GaussianBlur(0.8))

    return text, image