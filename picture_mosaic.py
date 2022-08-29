from PIL import Image
from os.path import join
from os import walk
import numpy as np

IMAGE = 'image.jpg'
MOSAIC = 'mosaic.png'
IMAGES = 'images'

MOSAIC_X_SIZE = 100
MOSAIC_Y_SIZE = 100

TILE_X_SIZE = 100
TILE_Y_SIZE = 100

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

def load_images():
    for root, dirs, files in walk(IMAGES):
        for file in files:
            try:
                img = Image.open(join(root, file))
            except Exception:
                pass
            else:
                yield crop_center(img, TILE_X_SIZE, TILE_Y_SIZE)

def get_dominant_color(img):
    img = np.array(img).reshape(-1, 3)
    return tuple(round(v) for v in img.mean(axis=0))

def get_colors_and_images():
    return tuple((get_dominant_color(img), img) for img in load_images())

def get_image(images, color):
    best_img = None
    best_color = None
    dist = 1000
    for avg_color, img in images:
        new_dist = abs(color[0] - avg_color[0]) + abs(color[1] - avg_color[1]) + abs(color[2] - avg_color[2])
        if new_dist < dist:
            best_img = img
            best_color = avg_color
            dist = new_dist
    diff = (color[0] - best_color[0], (color[1] - best_color[1], (color[2] - best_color[2])
    return best

def main():
    print('Loading main image')
    image = Image.open(IMAGE)
    image = crop_center(image, MOSAIC_X_SIZE, MOSAIC_Y_SIZE)
    print('Loading images')
    images = get_colors_and_images()
    print(f'Loaded {len(images)} images')
    

if __name__ == '__main__':
    main()