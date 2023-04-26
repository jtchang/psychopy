import zarr
import skimage.io as io
from skimage.transform import resize
import numpy as np
import skimage.color
from pathlib import Path
from tqdm import tqdm
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile


def rescale_img(idx_start, idx_stop, files):
    img_stack = np.empty((idx_stop-idx_start, 800, 800), dtype=np.uint8)

    for idx, file in enumerate(files):
        img = io.imread(str(file), as_gray=True)

        if img.shape[0] != 0 or img.shape[1] != 0:
            img = resize(img, (800, 800), anti_aliasing=True)

        max_pix = img.max()
        min_pix = img.min()

        img = (img-min_pix)/(max_pix-min_pix) * 255.0  # scale 0-255

        mean_pix = img.mean()
        while np.abs(mean_pix - 128.0) > 0.01:
            img = img-mean_pix + 128.0
            img[img > 255] = 255
            img[img < 0] = 0
            mean_pix = img.mean()
        img_stack[idx, :, :] = img.astype(np.uint8)
    return idx_start, idx_stop, img_stack


if __name__ == '__main__':
    zipurl = "https://things-initiative.org/uploads/THINGS/images.zip"

    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('/tmp/ThingsDB')

            things_db = '/tmp/ThingsDB'
            chunk_size = 1000
            # screen for all 800x800 images

            files = list(Path(things_db).rglob(('*.jpg')))

            # we'll skip some categories that don't have interesting images
            store = zarr.DirectoryStore('natural_scenes_THINK.zarr', normalize_keys=True)
            image_zarr = zarr.zeros(shape=(len(files), 800, 800),
                                    chunks=(chunk_size, 800, 800), dtype=np.uint8, store=store, overwrite=True)
            # shuffle with a seed to get repeatable results
            random.Random(255).shuffle(files)

            with ProcessPoolExecutor(max_workers=6) as pool:
                with tqdm(total=len(files)//chunk_size) as progress:
                    futures = []
                    for idx_start in np.arange(0, len(files), chunk_size, dtype=np.uint8):
                        idx_stop = idx_start + chunk_size

                        if idx_stop > len(files):
                            idx_stop = len(files)

                        future = pool.submit(rescale_img, idx_start, idx_stop, files[idx_start:idx_stop])
                        futures.append(future)

                    for future in as_completed(futures):
                        idx_start, idx_stop, img = future.result()
                        image_zarr[idx_start:idx_stop, :, :] = img
                        del future
                        progress.update(1)
