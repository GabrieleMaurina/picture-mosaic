from PIL import Image, ImageOps
from os.path import join, basename
from os import walk
import numpy as np
from progressbar import progressbar
from random import choice

INPUT = 'input'
OUTPUT = 'output'
TILES = 'tiles'
#TILES = 'tiles/Baby Wu Dijing'

MOSAIC_X_SIZE = 300
MOSAIC_Y_SIZE = 300

TILE_X_SIZE = 100
TILE_Y_SIZE = 100

N_TILES = 10

def crop_center(img, new_x, new_y):
    old_x, old_y = img.size
    old_ratio = old_x / old_y
    new_ratio = new_x / new_y
    if old_ratio > new_ratio:
        x = new_ratio * old_y
        dx = (old_x - x) // 2
        img = img.crop((dx, 0, dx + x, old_y))
    elif old_ratio < new_ratio:
        y = old_x / new_ratio
        dy = (old_y - y) // 2
        img = img.crop((0, dy, old_x, dy + y))
    return img.resize((new_x, new_y))

def find_images(path):
    for root, dirs, files in walk(path):
        for file in files:
            yield join(root, file)

def get_average_color(img):
    return tuple(round(v) for v in img.mean(axis=(0, 1)))

def load_tiles():
    tiles = []
    for img in progressbar(tuple(find_images(TILES))):
        try:
            img = Image.open(img)
        except Exception:
            pass
        else:
            tile = np.asarray(crop_center(ImageOps.exif_transpose(img).convert('RGB'), TILE_X_SIZE, TILE_Y_SIZE))
            color = get_average_color(tile)
            tiles.append((color, tile))
    return tiles

def get_best(ranked):
    best_dist = ranked[0][0]
    best = []
    for dist, avg_color, tile in ranked:
        if dist == best_dist:
            best.append((dist, avg_color, tile))
        else: break
    if len(best) < N_TILES:
        best = ranked[:N_TILES]
    return choice(best)

def get_tile(tiles, color):
    ranked = [(abs(color[0] - avg_color[0]) + abs(color[1] - avg_color[1]) + abs(color[2] - avg_color[2]), avg_color, tile) for avg_color, tile in tiles]
    ranked.sort(key=lambda v: v[0])
    dist, avg_color, tile = get_best(ranked)
    
    diff = np.array((color[0] - avg_color[0], color[1] - avg_color[1], color[2] - avg_color[2]), dtype=np.int16)
    tile = np.add(tile, diff).clip(0, 255).astype(np.uint8)
    return Image.fromarray(tile)

def generate_mosaic(image, tiles):
    mosaic = Image.new('RGB', (MOSAIC_X_SIZE * TILE_X_SIZE, MOSAIC_Y_SIZE * TILE_Y_SIZE))
    x_size, y_size = image.size
    coords = [(x,y) for x in range(x_size) for y in range(y_size)]
    for x, y in progressbar(coords):
        x_pos = x * TILE_X_SIZE
        y_pos = y * TILE_Y_SIZE
        tile = get_tile(tiles, image.getpixel((x, y)))
        mosaic.paste(tile, (x_pos, y_pos, x_pos + TILE_X_SIZE, y_pos + TILE_Y_SIZE))
    return mosaic

def main():
    print('Loading tiles')
    tiles = load_tiles()
    print('Generating mosaics')
    for img in find_images(INPUT):
        name = basename(img.rsplit('.', 1)[0])
        print(name)
        image = crop_center(ImageOps.exif_transpose(Image.open(img)).convert('RGB'), MOSAIC_X_SIZE, MOSAIC_Y_SIZE)
        generate_mosaic(image, tiles).save(join(OUTPUT, name) + '.png')

if __name__ == '__main__':
    main()