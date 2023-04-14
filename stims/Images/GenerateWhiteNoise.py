import numpy as np
import zarr

if __name__ == '__main__':

    noise_zarr = zarr.open('./stims/images/DenseNoise.zarr',
                           mode='w',
                           shape=(9000, 16, 16),
                           chunks=(2000, 16, 16), dtype=np.float32)

    noise_zarr[:, :, :] = np.random.randint(0, 2, size=(9000, 16, 16))
    noise_zarr[:, :, :] = (noise_zarr[:, :, :] * 2) - 1
