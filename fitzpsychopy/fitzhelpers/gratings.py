import numpy as np
from psychopy import visual


def makeGratingTexture(stim_settings):

    if stim_settings['texture_type'] == 'sqrDutyCycle':
        return sqrDutyCycle(stim_settings['duty_cycle'],
                            stim_settings['foreground_color'])
    elif stim_settings['texture_type'] == 'lumSin':
        return lumSin(stim_settings['minv'],
                      stim_settings['maxv'])
    else:
        return stim_settings['texture_type'], -90, None


def sqrDutyCycle(duty_cycle, foreground_color):

    textureType = np.ones((duty_cycle, 1))
    textureType[1, :] = -1
    textureType = foreground_color * textureType

    ori_shift_val = 0

    return textureType, ori_shift_val, None


def lumSin(minv, maxv):

    nr = (np.array([minv, maxv]) * 2)-1
    rg = nr[1]-nr[0]
    x = np.linspace(0, 2*np.pi, 256, False)
    y = np.expand_dims(((np.sin(x)+1.0)/2.0) * rg+nr[0], axis=1)

    barTexture = np.mean(nr) * np.ones([256, 256, 3])

    return y, 0, barTexture


def lumSqr(minv, maxv):
    nr = (np.array([minv, maxv]) * 2)-1
  
    barTexture = np.mean(nr) * np.ones((256, 256, 3))
    
    return nr.T, 0, barTexture
    