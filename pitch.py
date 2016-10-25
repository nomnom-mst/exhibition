#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import wave
import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as scw
import matplotlib.pyplot as plt


# 自己相関関数
def auto_correlate(arr):
    result = sig.correlate(arr,arr,mode="full")
    return result[result.size/2:]


# 相互相関関数
def correlate(arr):
    return sig.correlate(arr[:N+max_m],arr[:N],mode="valid")


def find_first_peak(arr):
    i = 0
    while arr[i] > arr[i+1]:
        i += 1
    while arr[i] < arr[i+1]:
        i += 1
    return i


def find_peaks(arr, local_width=1, min_peak_distance=1):
    """
    閾値と極大・極小を判定する窓幅、ピーク間最小距離を与えて配列からピークを検出する。
    内部的にはピーク間距離は正負で区別して算出されるため、近接した正負のピークは検出される。
    :rtype (int, float)
    :return tuple (ndarray of peak indices, ndarray of peak value)
    """
    # generate candidate indices to limit by threthold
    #idxs = np.where(np.abs(arr) > amp_thre)[0]
    idxs = np.arange(0, len(arr))

    # extend array to decide local maxima/minimum
    idxs_with_offset = idxs + local_width
    arr_extend = np.r_[[arr[0]] * local_width, arr, [arr[-1]] * local_width]

    last_pos_peak_idx = 0
    last_neg_peak_idx = 0
    result_idxs = []

    for i in idxs_with_offset:
        is_local_maximum = (arr_extend[i] >= 0 and
                            arr_extend[i] >= np.max(arr_extend[i - local_width: i + local_width + 1]))
        is_local_minimum = (arr_extend[i] <  0 and
                            arr_extend[i] <= np.min(arr_extend[i - local_width: i + local_width + 1]))
        if (is_local_maximum or is_local_minimum):
            if is_local_minimum:
                if i - last_pos_peak_idx > min_peak_distance:
                    result_idxs.append(i)
                    last_pos_peak_idx = i
            else:
                if i - last_neg_peak_idx > min_peak_distance:
                    result_idxs.append(i)
                    last_neg_peak_idx = i

    result_idxs = np.array(result_idxs) - local_width
    return (result_idxs, arr[result_idxs])


def calc_pitch(data, samp_rate):
    data = data / (2 ** 15)
    delta_time = 1. / samp_rate
   
    # 自己相関係数の計算
    win_size = 2 ** 9 # 512
    N = 2 ** 9
    start = 1000
   
    cor = auto_correlate(data[start:start+N])
    peak_index = find_first_peak(cor)
    freq = 1 / (peak_index * delta_time)
    print(freq)

    plt.plot(np.arange(cor.size) * delta_time, cor)
    plt.show()
