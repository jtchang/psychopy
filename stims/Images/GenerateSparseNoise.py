import numpy as np
import zarr
from numpy.linalg import norm

if __name__ == '__main__':
    x, y = [16, 16]
    min_distance = 6
    noise_zarr = zarr.open('./stims/images/SparseNoise.zarr',
                           mode='w',
                           shape=(10000, x+1, y+1),
                           chunks=(2000, x+1, y+1), dtype=np.float32)

    previous_xy = [[100, 100], [100, 100]]
    for i in range(noise_zarr.shape[0]):

        noise_zarr[i, :, :] = 0

        pos = np.random.randint(0, y, 2)

        while norm(pos-previous_xy[0]) < min_distance or norm(pos-previous_xy[1]) < min_distance:
            pos = np.random.randint(0, y, 2)

        color = [-1, 1][np.random.randint(0, 2)]

        noise_zarr[i, pos[0]:pos[0]+2, pos[1]:pos[1]+2] = color

        second_pos = np.random.randint(0, y, 2)

        while norm(pos - second_pos) < min_distance or norm(pos-previous_xy[0]) < min_distance or norm(pos-previous_xy[1]) < min_distance:
            second_pos = np.random.randint(0, y, 2)

        color = [-1, 1][np.random.randint(0, 2)]

        noise_zarr[i, second_pos[0]:second_pos[0]+2, second_pos[1]:second_pos[1]+2] = color

        previous_xy = [pos, second_pos]
