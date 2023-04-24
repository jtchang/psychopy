import numpy as np
import zarr

if __name__ == '__main__':

    noise_zarr = zarr.open('./stims/images/DenseNoiseFullScreen.zarr',
                           mode='w',
                           shape=(9000, 60, 106),
                           chunks=(2000, 60, 106), dtype=np.float32)

    noise_zarr[:, :, :] = np.random.randint(0, 2, size=(9000, 60, 106))
    noise_zarr[:, :, :] = (noise_zarr[:, :, :] * 2) - 1
