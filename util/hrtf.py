"""
spatialize a sound in azimuth and elevation
"""
import numpy as np
import scipy.io.wavfile as wav_file
from scipy.signal import lfilter
import os


def readHRTF(name):
    """Read the hrtf data from compact format files"""
    r = np.fromfile(name, np.dtype('>i2'), 256)
    r.shape = (128, 2)
    # half the rate to 22050 and scale to 0 -> 1
    r = r.astype(float)
    # should use a better filter here, this is a box lowering the sample rate from 44100 to 22050
    r = (r[0::2, :] + r[1::2, :]) / 65536
    return r


def generate_3d(rate, mono_sound, save_dir):
    for elev in range(-40, 100, 10):
        if elev != 0:
            print(f"{elev} is not 0 and skip..")
            continue
        elev_dir = os.path.join(r"../compact", "elev" + str(elev))  # download from http://sound.media.mit.edu/resources/KEMAR/compact.tar.Z
        if not os.path.exists(elev_dir):
            print(f"elevation {elev_dir} not found so skip..")
            continue
        for azimuth in range(0, 181):
            az = str(azimuth).zfill(3)
            hrtf_file = os.path.join(elev_dir, "H" + str(elev) + "e" + str(az) + "a.dat")
            if not os.path.exists(hrtf_file):
                print(f"hrtf_file {hrtf_file} not found so skip..")
                continue
            hrtf = readHRTF(hrtf_file)
            left = lfilter(hrtf[:, 0], 1.0, mono_sound)
            right = lfilter(hrtf[:, 1], 1.0, mono_sound)
            result = np.array([left, right]).T.astype(np.int16)
            oname = os.path.join(save_dir, str(elev) + "+A" + str(az))
            p = oname + '.wav'
            print(p)
            wav_file.write(p, rate, result)
            result = result[:, (1, 0)]
            # save a wav
            oname = os.path.join(save_dir, str(elev) + "+A-" + str(az))
            p = oname + '.wav'
            print(p)
            wav_file.write(p, rate, result)


# 1 define save dir
save_name_ = r"../materials/HRTF"
if not os.path.exists(save_name_):
    os.mkdir(save_name_)

# 2 install sox
# install "sox"
# add sox to path

#
# 3 CMD run sox trans wav to wav
# cd path_XXX
# sox sin_100-1_hz.wav -r 22050 -c 1 -b 16 sin_100-1_hz_sox.wav

# 4 read sound 1 and generate 3D sounds
# read the input
rate_, mono_sound_ = wav_file.read(r"../materials/300.wav")
generate_3d(rate_, mono_sound_, save_name_)
# sox sin_1100-1_hz.wav -r 22050 -c 1 -b 16 sin_1100-1_hz_sox.wav
