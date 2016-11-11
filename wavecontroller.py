#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import os
import wave
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import array


def show_image(data):
    plt.figure(figsize=(18,4))
    plt.plot(data)
    plt.show()
    

def show_info(wavefile):
    wf = wave.open(wavefile, "r")

    """WAVEファイルの情報を取得"""
    print "チャンネル数:", wf.getnchannels()
    print "サンプル幅:", wf.getsampwidth()
    print "サンプリング周波数:", wf.getframerate()
    print "フレーム数:", wf.getnframes()
    print "パラメータ:", wf.getparams()
    print "長さ（秒）:", float(wf.getnframes()) / wf.getframerate()

    wf.close()


def get_data(wavefile):
    wf = wave.open(wavefile, "r")
    
    buf = wf.readframes(wf.getnframes())
    data = np.frombuffer(buf, dtype="int16")

    wf.close()

    return data


def smoothing(data, roughness):
    pre_amp = np.mean(abs(data))
    
    kernel = np.ones(roughness)/roughness
    data = np.convolve(data, kernel, mode="same")
    
    kernel = np.ones(4)/4
    for _ in range(100):
        data = np.convolve(data, kernel, mode="same")

    amp = np.mean(abs(data))
    data *= pre_amp/amp/2
    
    return data.astype(np.int16)


def calc_amp(data):
    local_width = 1000
    
    idxs = np.arange(0, len(data))
    data = abs(data)

    # extend array to decide local maxima/minimum
    idxs_with_offset = idxs + local_width
    data_extend = np.r_[[data[0]] * local_width, data]

    amps = []

    for i in idxs_with_offset:
        amps.append(np.max(data_extend[i - local_width: i + 1]))

    amps = amps[:-local_width] / np.max(amps).astype(float)
    
    return amps


def save_file(wavefile, data, fs):
    if os.path.exists(wavefile):
        os.remove(wavefile)
    
    wf = wave.Wave_write(wavefile)
    wf.setparams((2,                       # channel
                  2,                       # byte width
                  fs,                      # sampling rate
                  len(data),               # number of frames
                  "NONE", "not compressed" # no compression
                  ))
    wf.writeframes(array.array("h", data).tostring())
    wf.close()
