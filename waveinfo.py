#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import os
import wave
import numpy as np
import matplotlib.pyplot as plt
import array


def show_image(data):
    plt.figure(figsize=(18,4))
    plt.plot(np.arange(0, 1000), data[:1000])
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


def get_smoothed_data(wavefile):
    wf = wave.open(wavefile, "r")
    
    buf = wf.readframes(wf.getnframes())
    data = np.frombuffer(buf, dtype="int16")

    kernel = np.ones(50)/50
    for _ in range(10):
        data = np.convolve(data, kernel, mode="same")

    wf.close()

    return data.astype(np.int16)


def save_file(wavefile, data):
    if os.path.exists(wavefile):
        os.remove(wavefile)
    
    wf = wave.Wave_write(wavefile)
    wf.setparams((2,                       # channel
                  2,                       # byte width
                  44100,                   # sampling rate
                  len(data),               # number of frames
                  "NONE", "not compressed" # no compression
                  ))
    wf.writeframes(array.array("h", data).tostring())
    wf.close()    
