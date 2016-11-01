#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import wavecontroller
import numpy as np

SAMPLE_FREQ = 44100
PITCH_FRAME = 80
REDUCTION = 50
nazo = 5


def pitch2freq(pitch_data):
    return np.array(map(lambda n:SAMPLE_FREQ/n if not n==0 else 0, pitch_data))


def sin_wave(freq_data):    
    results = []
    
    # [-1.0, 1.0]の小数値が入った波を作成
    for i,f0 in enumerate(freq_data):
        if i%REDUCTION!=0:
            continue
        for j in np.arange(PITCH_FRAME*REDUCTION):
            signal = np.sin(2 * np.pi * f0 * (i*PITCH_FRAME + j) / nazo / (SAMPLE_FREQ/PITCH_FRAME))
            # 振幅が大きい時はクリッピング
            if signal > 1.0:  signal = 1.0
            if signal < -1.0: signal = -1.0
            results.append(signal)
        
    # [-32768, 32767]の整数値に変換
    results = np.array(map(lambda n:int(n * 32767.0), results))

    return results
