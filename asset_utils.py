import sys
from pathlib import Path

import pygame


def get_project_root() -> Path:
    return Path(__file__).resolve().parent


def resource_path(relative_path: str) -> str:
    meipass = getattr(sys, "_MEIPASS", None)
    if isinstance(meipass, str):
        return str(Path(meipass) / relative_path)

    return str(get_project_root() / relative_path)


def load_image_with_aspect_ratio(image_path, max_width, max_height):
    image = pygame.image.load(resource_path(image_path)).convert_alpha()

    original_width = image.get_width()
    original_height = image.get_height()

    if original_width == 0 or original_height == 0:
        return image

    scale_ratio = min(
        max_width / original_width,
        max_height / original_height,
    )

    scaled_width = max(1, int(original_width * scale_ratio))
    scaled_height = max(1, int(original_height * scale_ratio))

    return pygame.transform.smoothscale(
        image,
        (scaled_width, scaled_height),
    )
