import asyncio
import hashlib
import math
import os
import textwrap
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont


class LocalImageGenerator:
    """Creates polished local story cards without a paid image API."""

    def __init__(self, asset_dir: Optional[Path] = None):
        self.asset_dir = Path(asset_dir or Path("outputs") / "generated_assets")
        self.asset_dir.mkdir(parents=True, exist_ok=True)

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        creator_name: str = "Ayett",
    ) -> str:
        return await asyncio.to_thread(
            self._render_card,
            prompt,
            aspect_ratio,
            creator_name,
            None,
        )

    async def generate_image_with_reference(
        self,
        prompt: str,
        reference_url: str,
        aspect_ratio: str = "16:9",
        creator_name: str = "Ayett",
    ) -> str:
        reference_path = Path(reference_url)
        return await asyncio.to_thread(
            self._render_card,
            prompt,
            aspect_ratio,
            creator_name,
            reference_path if reference_path.exists() else None,
        )

    def _render_card(
        self,
        prompt: str,
        aspect_ratio: str,
        creator_name: str,
        reference_path: Optional[Path],
    ) -> str:
        width, height = self._size_for_ratio(aspect_ratio)
        digest = hashlib.sha256(prompt.encode("utf-8", errors="ignore")).digest()
        palette = self._palette(digest)

        canvas = Image.new("RGB", (width, height), palette[0])
        pixels = canvas.load()
        for y in range(height):
            ratio = y / max(height - 1, 1)
            for x in range(width):
                horizontal = x / max(width - 1, 1)
                blend = min(1.0, 0.65 * ratio + 0.35 * horizontal)
                pixels[x, y] = tuple(
                    int(palette[0][i] * (1 - blend) + palette[1][i] * blend)
                    for i in range(3)
                )

        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow = ImageDraw.Draw(glow_layer)
        for idx in range(6):
            radius = int(min(width, height) * (0.12 + idx * 0.045))
            cx = int(width * (0.14 + ((digest[idx] / 255) * 0.76)))
            cy = int(height * (0.16 + ((digest[idx + 6] / 255) * 0.68)))
            color = palette[2 + (idx % 2)] + (34,)
            glow.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=max(16, width // 35)))
        canvas = Image.alpha_composite(canvas.convert("RGBA"), glow_layer)

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        margin = int(width * 0.055)
        green = (29, 185, 84, 255)
        ink = (25, 20, 20, 255)
        white = (255, 255, 255, 255)
        soft_white = (255, 255, 255, 228)

        # Spotify-inspired light editorial panel.
        panel_left = margin
        panel_top = int(height * 0.12)
        panel_right = int(width * 0.68)
        panel_bottom = int(height * 0.88)
        draw.rounded_rectangle(
            (panel_left, panel_top, panel_right, panel_bottom),
            radius=max(22, width // 42),
            fill=(255, 255, 255, 225),
            outline=(255, 255, 255, 245),
            width=2,
        )

        # Character or abstract portrait disc.
        portrait_size = int(min(width, height) * 0.42)
        px = int(width * 0.73)
        py = int(height * 0.5)
        portrait_box = (
            px - portrait_size // 2,
            py - portrait_size // 2,
            px + portrait_size // 2,
            py + portrait_size // 2,
        )
        draw.ellipse(portrait_box, fill=(245, 245, 242, 245), outline=white, width=max(4, width // 180))

        if reference_path:
            try:
                reference = Image.open(reference_path).convert("RGB")
                reference = self._fit_cover(reference, portrait_size, portrait_size)
                mask = Image.new("L", (portrait_size, portrait_size), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, portrait_size, portrait_size), fill=255)
                overlay.paste(reference.convert("RGBA"), (portrait_box[0], portrait_box[1]), mask)
            except Exception:
                self._draw_silhouette(draw, portrait_box, digest)
        else:
            self._draw_silhouette(draw, portrait_box, digest)

        display_title = self._title_from_prompt(prompt)
        body = self._body_from_prompt(prompt, display_title)
        title_font = self._font(max(34, width // 24), bold=True)
        body_font = self._font(max(20, width // 55), bold=False)
        small_font = self._font(max(15, width // 78), bold=True)

        tag = "AYETT STORIES"
        draw.rounded_rectangle(
            (panel_left + 28, panel_top + 26, panel_left + 210, panel_top + 68),
            radius=20,
            fill=green,
        )
        draw.text((panel_left + 48, panel_top + 36), tag, font=small_font, fill=white)

        text_x = panel_left + 34
        text_y = panel_top + 105
        max_text_width = panel_right - text_x - 34
        title_lines = self._wrap_pixels(display_title, title_font, max_text_width, max_lines=3)
        for line in title_lines:
            draw.text((text_x, text_y), line, font=title_font, fill=ink)
            text_y += int(title_font.size * 1.18)

        text_y += 18
        body_lines = self._wrap_pixels(body, body_font, max_text_width, max_lines=5)
        for line in body_lines:
            draw.text((text_x, text_y), line, font=body_font, fill=(72, 72, 72, 255))
            text_y += int(body_font.size * 1.42)

        footer = f"A free local visual by {creator_name or 'Ayett'}"
        draw.text((text_x, panel_bottom - 58), footer, font=small_font, fill=(96, 96, 96, 255))
        draw.ellipse((panel_right - 74, panel_bottom - 78, panel_right - 26, panel_bottom - 30), fill=green)
        draw.polygon(
            [
                (panel_right - 55, panel_bottom - 66),
                (panel_right - 55, panel_bottom - 42),
                (panel_right - 37, panel_bottom - 54),
            ],
            fill=white,
        )

        # Subtle top light and grain.
        draw.rectangle((0, 0, width, int(height * 0.08)), fill=soft_white)
        canvas = Image.alpha_composite(canvas, overlay).convert("RGB")

        filename = f"frame_{uuid.uuid4().hex}.jpg"
        output = self.asset_dir / filename
        canvas.save(output, quality=92, optimize=True)
        return str(output)

    @staticmethod
    def _size_for_ratio(aspect_ratio: str) -> tuple[int, int]:
        if aspect_ratio == "2:3":
            return 768, 1152
        if aspect_ratio == "1:1":
            return 1024, 1024
        return 1280, 720

    @staticmethod
    def _palette(digest: bytes):
        palettes = [
            ((234, 250, 239), (191, 238, 207), (29, 185, 84), (124, 220, 157)),
            ((249, 246, 232), (229, 242, 215), (29, 185, 84), (246, 194, 92)),
            ((239, 247, 255), (218, 238, 232), (29, 185, 84), (106, 171, 255)),
            ((251, 238, 244), (226, 243, 232), (29, 185, 84), (238, 125, 166)),
        ]
        return palettes[digest[0] % len(palettes)]

    @staticmethod
    def _title_from_prompt(prompt: str) -> str:
        cleaned = " ".join(prompt.replace("\n", " ").split())
        first = cleaned.split(".")[0].strip()
        return (first[:92] or "A new scene").strip()

    @staticmethod
    def _body_from_prompt(prompt: str, title: str) -> str:
        cleaned = " ".join(prompt.replace("\n", " ").split())
        remainder = cleaned[len(title):].lstrip(". ")
        return remainder[:260] or "A cinematic moment shaped into a clean, locally generated story card."

    @staticmethod
    def _fit_cover(image: Image.Image, width: int, height: int) -> Image.Image:
        scale = max(width / image.width, height / image.height)
        resized = image.resize((int(image.width * scale), int(image.height * scale)), Image.Resampling.LANCZOS)
        left = max(0, (resized.width - width) // 2)
        top = max(0, (resized.height - height) // 2)
        return resized.crop((left, top, left + width, top + height))

    @staticmethod
    def _draw_silhouette(draw: ImageDraw.ImageDraw, box, digest: bytes) -> None:
        left, top, right, bottom = box
        width = right - left
        height = bottom - top
        skin_options = [(105, 74, 57, 255), (176, 126, 93, 255), (224, 179, 145, 255), (86, 55, 46, 255)]
        skin = skin_options[digest[2] % len(skin_options)]
        hair = [(37, 31, 30, 255), (70, 43, 28, 255), (30, 30, 42, 255)][digest[3] % 3]
        outfit = [(29, 185, 84, 255), (39, 39, 42, 255), (78, 124, 191, 255)][digest[4] % 3]
        head_r = int(width * 0.18)
        cx = (left + right) // 2
        head_cy = int(top + height * 0.35)
        draw.ellipse((cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r), fill=skin)
        draw.pieslice((cx - head_r - 4, head_cy - head_r - 8, cx + head_r + 4, head_cy + head_r), 180, 360, fill=hair)
        shoulder_top = int(top + height * 0.56)
        draw.rounded_rectangle((left + int(width * 0.18), shoulder_top, right - int(width * 0.18), bottom + 20), radius=int(width * 0.12), fill=outfit)

    @staticmethod
    def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return ImageFont.truetype(candidate, size=size)
        return ImageFont.load_default()

    @staticmethod
    def _wrap_pixels(text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if font.getlength(trial) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
                if len(lines) >= max_lines:
                    break
        if current and len(lines) < max_lines:
            lines.append(current)
        if len(lines) == max_lines and len(" ".join(lines)) < len(text):
            lines[-1] = lines[-1].rstrip(".,;: ") + "…"
        return lines
