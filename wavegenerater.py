#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import wavecontroller
import numpy as np

SAMPLE_FREQ = 44100
REDUCTION = 3
EMPH_FREQ = 1.4


def pitch2freq(pitch_data):
    return np.array(map(lambda n:SAMPLE_FREQ/n if not n==0 else 0, pitch_data))


def sin_wave(freq_data, amps, frame):
    results = []
    prev_offset = 0
    offset = 0
    prev_f0 = 0
    
    mean = np.mean(freq_data)
    not_zero_idxs = np.where(freq_data!=0)[0]
    freq_data[not_zero_idxs] = (freq_data[not_zero_idxs] - mean) * EMPH_FREQ + mean
    
    # [-1.0, 1.0]の小数値が入った波を作成
    for i,f0 in enumerate(freq_data):
        if i%REDUCTION!=0:
            continue

        t = float(i*frame) / SAMPLE_FREQ
        prev_phase = (2 * np.pi * prev_f0 * t + prev_offset)%(2 * np.pi)
        phase = (2 * np.pi * f0 * t)%(2 * np.pi)
        offset = prev_phase - phase
        
        for j in np.arange(frame*REDUCTION):
            t = float(i*frame + j) / SAMPLE_FREQ
            theta = 2 * np.pi * f0 * t + offset
            signal = amps[i*frame] * np.sin(theta)
            # 振幅が大きい時はクリッピング
            if signal > 1.0:  signal = 1.0
            if signal < -1.0: signal = -1.0
            results.append(signal)
        prev_offset = offset
        prev_f0 = f0

    # 最後無音挿入
    fade_count = 1000
    results = np.append(results, np.arange(fade_count)[::-1]*results[-1]/fade_count)
    
    # [-32768, 32767]の整数値に変換
    results = np.array(map(lambda n:int(n * 32767.0), results))

    return results
