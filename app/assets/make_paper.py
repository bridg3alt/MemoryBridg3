"""Draw the aged graph paper the app sits on, so the texture is ours and carries no watermark.

Everything is generated: the fibre, the grid, the creases, the foxing and the warm edge burn.
Run it to rebuild `paper-bg.jpg` after changing any of the numbers below.

    python app/assets/make_paper.py
"""
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE / "paper-bg.jpg"

SIZE = 1600
GRID = 44                      # spacing of the squares, in pixels
PAPER = (238, 228, 205)        # the aged cream the whole sheet starts from
GRID_INK = (150, 122, 84)
SEED = 1976                    # Thomas's record, so the sheet is the same every time


def fibre(size: int, rng: random.Random) -> Image.Image:
    """Paper is never flat: speckle it, then blur, so the grain sits under everything else."""
    noise = Image.new("L", (size // 2, size // 2))
    noise.putdata([rng.gauss(128, 26) for _ in range(noise.width * noise.height)])
    return noise.resize((size, size), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.6))


def creases(canvas: Image.Image, rng: random.Random) -> None:
    """A sheet that has been folded and carried around holds its creases."""
    shade = Image.new("L", canvas.size, 128)
    pen = ImageDraw.Draw(shade)
    for _ in range(7):
        x1, y1 = rng.randint(0, SIZE), rng.randint(0, SIZE)
        x2, y2 = x1 + rng.randint(-SIZE, SIZE), y1 + rng.randint(-SIZE, SIZE)
        pen.line((x1, y1, x2, y2), fill=rng.randint(96, 116), width=rng.randint(2, 5))
        pen.line((x1 + 3, y1 + 3, x2 + 3, y2 + 3), fill=rng.randint(140, 158), width=rng.randint(2, 4))
    shade = shade.filter(ImageFilter.GaussianBlur(3.5))
    canvas.paste(Image.composite(canvas.point(lambda v: max(0, v - 18)), canvas, shade.point(
        lambda v: 255 if v < 120 else 0)), (0, 0))


def foxing(canvas: Image.Image, rng: random.Random) -> None:
    """The brown blooms old paper develops where it was damp."""
    stains = Image.new("L", canvas.size, 0)
    pen = ImageDraw.Draw(stains)
    for _ in range(26):
        x, y = rng.randint(0, SIZE), rng.randint(0, SIZE)
        r = rng.randint(30, 150)
        pen.ellipse((x - r, y - r, x + r, y + r), fill=rng.randint(10, 34))
    stains = stains.filter(ImageFilter.GaussianBlur(40))
    tint = Image.new("RGB", canvas.size, (176, 142, 96))
    canvas.paste(Image.composite(tint, canvas, stains), (0, 0))


def main() -> None:
    rng = random.Random(SEED)

    sheet = Image.new("RGB", (SIZE, SIZE), PAPER)
    grain = fibre(SIZE, rng)
    sheet = Image.composite(sheet.point(lambda v: min(255, v + 10)),
                            sheet.point(lambda v: max(0, v - 10)), grain)

    # the grid, drawn faintly and then softened so it sits in the paper rather than on it
    lines = Image.new("RGB", (SIZE, SIZE), PAPER)
    pen = ImageDraw.Draw(lines)
    for i in range(0, SIZE + GRID, GRID):
        drift = rng.randint(-1, 1)                    # hand-cut paper is never perfectly square
        pen.line((i + drift, 0, i + drift, SIZE), fill=GRID_INK, width=1)
        pen.line((0, i + drift, SIZE, i + drift), fill=GRID_INK, width=1)
    lines = lines.filter(ImageFilter.GaussianBlur(0.4))
    sheet = Image.blend(sheet, lines, 0.34)

    foxing(sheet, rng)
    creases(sheet, rng)

    # warm burn towards the edges, the way old paper darkens where it was handled
    burn = Image.new("L", (SIZE, SIZE), 0)
    pen = ImageDraw.Draw(burn)
    # inset, so the blur leaves the edges dark: the mask keeps the clean sheet only in the middle
    pen.ellipse((SIZE * 0.10, SIZE * 0.10, SIZE * 0.90, SIZE * 0.90), fill=255)
    burn = burn.filter(ImageFilter.GaussianBlur(150))
    sheet = Image.composite(sheet, Image.blend(sheet, Image.new("RGB", sheet.size, (198, 168, 122)), .35), burn)

    sheet.save(OUT, "JPEG", quality=84, optimize=True)
    print(f"{OUT.name}: {SIZE}x{SIZE}, {OUT.stat().st_size / 1024:.0f} KB, seed {SEED}")


if __name__ == "__main__":
    main()
