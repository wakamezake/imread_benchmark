#!/usr/bin/env python3
import PIL.Image
import cv2
import imageio
import jpeg4py
import lycon
import numpy as np
import pathlib
import skimage.color
import skimage.io
import tensorflow as tf
import timeit
import torchvision

BASE_DIR = pathlib.Path(__file__).parent
# せめて日本語パスくらいには対応しててほしいので日本語ディレクトリ名
X1 = list(path for path in (BASE_DIR / 'で～た').glob('*')
          if path.suffix != ".gif")
X2 = list((BASE_DIR / 'で～た2').glob('*'))


def _main():
    functions = [
        imread_opencv,
        imread_pillow,
        imread_imageio,
        imread_skimage,
        imread_tf,
        imread_lycon,
        imread_torchvision
        # imread_jpeg4py
    ]

    # 速度計測
    loop = 300
    for i, x in enumerate(X1):
        print('=' * 32, x.name, '=' * 32)
        for f in functions:
            t = timeit.timeit('''f(x)''', number=loop, globals={'f': f, 'x': x})
            print(
                f'{f.__name__:15s}: {t:4.1f}[sec] (mean:{t / loop: .4f})[sec]')


def imread_opencv(path):
    arr = np.fromfile(str(path), np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None and path.suffix.lower() in ('.gif'):  # TODO
        video = cv2.VideoCapture(str(path))
        _, img = video.read()
    if img is None:
        return None
    return img[:, :, ::-1].astype(np.float32)


def imread_pillow(path):
    try:
        with PIL.Image.open(path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return np.asarray(img, dtype=np.float32)
    except BaseException:
        return None


def imread_imageio(path):
    try:
        img = imageio.imread(path)
        if len(img.shape) == 2:
            img = skimage.color.gray2rgb(img)
        elif img.shape[2] == 4:
            img = skimage.color.rgba2rgb(img)
    except BaseException:
        return None
    return img.astype(np.float32)


def imread_skimage(path):
    try:
        img = skimage.io.imread(path)
        if len(img.shape) == 2:
            img = skimage.color.gray2rgb(img)
        elif img.shape[2] == 4:
            img = skimage.color.rgba2rgb(img)
        return img.astype(np.float32)
    except BaseException:
        return None


def imread_tf(path):
    try:
        img = tf.io.read_file(str(path))
        img = tf.image.decode_image(img, channels=3)
    except BaseException:
        return None
    # https://www.tensorflow.org/api_docs/python/tf/io/decode_image
    # Note: decode_gif returns a 4-D array [num_frames, height, width, 3],
    if path.suffix == ".gif":
        return img.numpy()[0].astype(np.float32)
    else:
        return img.numpy().astype(np.float32)


def imread_lycon(path):
    try:
        img = lycon.load(str(path))
        # lycon can't load gif file
        if img is None:
            return None
        return img.astype(np.float32)
    except BaseException:
        return None


def imread_jpeg4py(path):
    try:
        img = jpeg4py.JPEG(str(path)).decode()
        # lycon can't load gif file
        if img is None:
            return None
        return img.astype(np.float32)
    except BaseException:
        return None


def imread_torchvision(path):
    # https://pytorch.org/docs/stable/torchvision/io.html#image
    try:
        # Tensor
        tensor = torchvision.io.read_image(str(path))
        # to numpy ndarray
        img = tensor.to('cpu').detach().numpy().copy()
        # (3, h, w) to (w, h, 3)
        img = img.transpose(1, 2, 0)
        if img is None:
            return None
        return img.astype(np.float32)
    except BaseException:
        return None


if __name__ == '__main__':
    _main()
