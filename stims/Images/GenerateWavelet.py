import numpy as np
import scipy.sparse
import zarr

from dtcwt import idualtree3D

def idualtree3D(w, J, Fsf, sf):
    """ Inverse 3D Dual-Tree Discrete Wavelet Transform.
    
    
    Ported from from https://eeweb.engineering.nyu.edu/iselesni/WaveletSoftware/

    Args:
        w (_type_): wavelet coefficients
        J (_type_): number of Stages
        Fsf (_type_): synthesis filter for the last stage
        sf (_type_): synthesis filters for the preceding stages
    """
    
    
    for k in range(J):
        for m in range(7):
            []

if __name__ == '__main__':

    sparse_noise = scipy.sparse.random()
        