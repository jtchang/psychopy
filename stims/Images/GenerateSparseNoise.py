import numpy as np
import zarr
from numpy.linalg import norm
from tqdm import tqdm
if __name__ == '__main__':
    x, y = [59, 105]
    min_distance = 6  # pixels
    num_boxes = 8
    noise_zarr = zarr.open('./stims/images/SparseNoise_fullscreen.zarr',
                           mode='w',
                           shape=(10000, x+1, y+1),
                           chunks=(2000, x+1, y+1), dtype=np.float32)
    previous_xy = np.full((num_boxes, 2), 1000)

    for i in tqdm(range(noise_zarr.shape[0])):

        noise_zarr[i, :, :] = 0
        current_positions = np.full((num_boxes, 2), 1000)
        for pos_idx in range(num_boxes):

            valid_pos = False

            while not valid_pos:
                pos = [np.random.randint(0, x),
                       np.random.randint(0, y)]

                far_previous = all([norm(pos-prev) > min_distance for prev in previous_xy])
                far_current = all([norm(pos - curr) > min_distance for curr in current_positions])

                valid_pos = far_previous and far_current

            if valid_pos:
                noise_zarr[i, pos[0]:pos[0]+2, pos[1]:pos[1]+2] = [1, -1][np.random.randint(0, 2)]
                current_positions[pos_idx, :] = pos

        previous_xy = current_positions.copy()

        """pos = np.random.randint(0, y, 2)

        while norm(pos-previous_xy[0]) < min_distance or norm(pos-previous_xy[1]) < min_distance:
            pos = np.random.randint(0, y, 2)

        color = [-1, 1][np.random.randint(0, 2)]

        noise_zarr[i, pos[0]:pos[0]+2, pos[1]:pos[1]+2] = color

        second_pos = np.random.randint(0, y, 2)

        while norm(pos - second_pos) < min_distance or norm(pos-previous_xy[0]) < min_distance or norm(pos-previous_xy[1]) < min_distance:
            second_pos = np.random.randint(0, y, 2)

        color = [-1, 1][np.random.randint(0, 2)]

        noise_zarr[i, second_pos[0]:second_pos[0]+2, second_pos[1]:second_pos[1]+2] = color

        previous_xy = [pos, second_pos]"""
