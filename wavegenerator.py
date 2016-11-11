#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import wavecontroller
import numpy as np


class generator:

    def __init__(self):
        self.sample_freq = 44100
        self.reduction = 3
        self.emph_freq = 1.4

        
    def pitch2freq(self, pitch_data, input_sample_freq):
        return np.array(map(lambda n:input_sample_freq/n if not n==0 else 0, pitch_data))


    def make_waves(self, wave, freq_data, amps, frame):
        EMPH_AMP = 0.9
        results = []
        data_list = []
        prev_offset = 0
        offset = 0
        prev_f0 = 0
        
        mean = np.mean(freq_data)
        not_zero_idxs = np.where(freq_data!=0)[0]
        freq_data[not_zero_idxs] = (freq_data[not_zero_idxs] - mean) * self.emph_freq + mean
    
        # [-1.0, 1.0]の小数値が入った波を作成
        overlap = int(frame*(self.reduction-0.5))
        for i,f0 in enumerate(freq_data):
            if i%self.reduction!=0:
                continue

            data = []
            t = float(i*frame) / self.sample_freq
            prev_phase = (2 * np.pi * prev_f0 * t + prev_offset)%(2 * np.pi)
            phase = (2 * np.pi * f0 * t)%(2 * np.pi)
            offset = prev_phase - phase
            amp = amps[i*frame]
        
            for j in np.arange(frame*self.reduction + overlap):
                t = float(i*frame + j) / self.sample_freq
                theta = 2 * np.pi * f0 * t + offset
                signal = (EMPH_AMP*amp + (1-EMPH_AMP)) * wave(theta) if f0!=0 else (1-EMPH_AMP)*wave(theta)
                # 振幅が大きい時はクリッピング
                if signal > 1.0:  signal = 1.0
                if signal < -1.0: signal = -1.0
                data = np.append(data, signal)

            data_list.append(data)
            prev_offset = offset
            prev_f0 = f0

        # クロスフェード
        results = self.crossfade(data_list, overlap)
        
        # 最後無音挿入
        fade_count = 1000
        results = np.append(results, np.arange(fade_count)[::-1]*results[-1]/fade_count)
    
        # [-32768, 32767]の整数値に変換
        results = np.array(map(lambda n:int(n * 32767.0), results))

        return results


    def make_combine_waves(self, wave, freq_data, amps, frame):
        EMPH_AMP = 0.7
        results = []
        data_list = []
        prev_offset = 0
        offset = 0
        prev_f0 = 0
        
        mean = np.mean(freq_data)
        not_zero_idxs = np.where(freq_data!=0)[0]
        freq_data[not_zero_idxs] = (freq_data[not_zero_idxs] - mean) * self.emph_freq + mean
    
        # [-1.0, 1.0]の小数値が入った波を作成
        overlap = int(frame*(self.reduction-0.5))
        for i,f0 in enumerate(freq_data):
            if i%self.reduction!=0:
                continue

            data = []
            t = float(i*frame) / self.sample_freq
            prev_phase = (2 * np.pi * prev_f0 * t + prev_offset)%(2 * np.pi)
            phase = (2 * np.pi * f0 * t)%(2 * np.pi)
            offset = prev_phase - phase
            amp = amps[i*frame]
        
            for j in np.arange(frame*self.reduction + overlap):
                t = float(i*frame + j) / self.sample_freq
                theta = 2 * np.pi * f0 * t + offset
                signal = (EMPH_AMP*amp + (1-EMPH_AMP))*wave(theta, amp) if f0!=0 else (1-EMPH_AMP)*wave(theta, 0)
                # 振幅が大きい時はクリッピング
                if signal > 1.0:  signal = 1.0
                if signal < -1.0: signal = -1.0
                data = np.append(data, signal)

            data_list.append(data)
            prev_offset = offset
            prev_f0 = f0

        # クロスフェード
        results = self.crossfade(data_list, overlap)
        
        # 最後無音挿入
        fade_count = 1000
        results = np.append(results, np.arange(fade_count)[::-1]*results[-1]/fade_count)
    
        # [-32768, 32767]の整数値に変換
        results = np.array(map(lambda n:int(n * 32767.0), results))

        return results


    def crossfade(self, data_list, overlap):
        results = []
        results = np.r_[results, data_list[0][:overlap]]
        for data1, data2 in zip(data_list[:-1], data_list[1:]):
            data1[-1*overlap:] = data1[-1*overlap:] * np.linspace(1, 0, overlap)
            data2[:overlap] = data2[:overlap] * np.linspace(0, 1, overlap)
            data = np.r_[data1[overlap:-1*overlap], data1[-1*overlap:]+data2[:overlap]]
            results = np.append(results, data)
        else:
            results = np.append(results, data_list[-1][overlap:-1*overlap])

        return results


    def sin_wave(self, theta):
        return np.sin(theta)


    def square_wave(self, theta):
        signal = 0.
        for k in np.arange(1,10):
            signal += np.sin((2*k-1) * theta) / (2*k-1)

        return signal


    def sawtooth_wave(self, theta):
        signal = 0.
        for k in range(1,10):
            signal += np.sin(k * theta) / k / 2

        return signal

    
    def triangle_wave(self, theta):
        signal = 0.
        for k in range(0,10):
            signal += (-1)**k * np.sin((2*k+1) * theta) / (2*k+1)**2 * 0.8

        return signal

    
    def sin_square_wave(self, theta, degree):
        signal = 0.
        n = 10
        for k in np.arange(1,int(n*degree)+2):
            signal += np.sin((2*k-1) * theta) / (2*k-1)

        return signal

    def sin_triangle_wave(self, theta, degree):
        signal = 0.
        n = 10
        for k in range(0,int(n*degree)+1):
            signal += (-1)**k * np.sin((2*k+1) * theta) / (2*k+1)**2 * 0.8

        return signal

    def sin_sawtooth_wave(self, theta, degree):
        signal = 0.
        n = 10
        for k in range(1,int(n*degree)+2):
            signal += np.sin(k * theta) / k / 2

        return signal
