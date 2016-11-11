#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import numpy as np
import bufconv


ZERO_LENGTH_THRESH = 100


def smoothing(data):
    pre_amp = np.mean(abs(data))

    kernel_size = 5
    extend_data = np.r_[ [data[0]]*kernel_size, data, [data[-1]]*kernel_size ]
    kernel = np.ones(kernel_size)/kernel_size
    for _ in range(100):
        extend_data = np.convolve(extend_data, kernel, mode="same")
        extend_data[:kernel_size] = [extend_data[kernel_size]]*kernel_size
        extend_data[-1*kernel_size:] = [extend_data[-1*kernel_size-1]]*kernel_size
    data = extend_data[kernel_size:-1*kernel_size]

    amp = np.mean(abs(data))
    data *= pre_amp/amp
    
    return data.astype(np.int16)


def split(data):
    remove_idxs = []
    
    ## trim
    start_idx = 0
    for value in data:
        start_idx += 1
        if not value==0:
            break
        
    end_idx = len(data)
    for value in data[::-1]:
        if not value==0:
            break
        end_idx -= 1

    remove_idxs = np.append(remove_idxs, np.arange(start_idx))
    remove_idxs = np.append(remove_idxs, np.arange(end_idx, len(data)))
    data = data[start_idx:end_idx]
    
    ## split
    zero_idxs = np.where(data==0)[0]
    arrs = []
    arr = []
    for i in np.arange(len(zero_idxs[1:])):
        arr.append(zero_idxs[i-1])
        if not zero_idxs[i] == zero_idxs[i-1]+1:
            arrs.append(arr[:])
            del arr[:]
    else:
        try:
            if not zero_idxs[i] == zero_idxs[i-1]+1:
                arrs.append(arr[:])
                del arr[:]
            arr.append(zero_idxs[-1])
            arrs.append(arr[:])
        except UnboundLocalError:
            pass
    arrs = np.array(arrs)
    
    interval_idxs = filter(lambda n:len(n)>ZERO_LENGTH_THRESH, arrs)
    interval_length = map(lambda n:len(n), interval_idxs)
    split_idxs = np.array(np.array(map(lambda n:[n[0],n[-1]+1], interval_idxs)).flat)

    data_list = []
    if not len(split_idxs)==0:
        data_list.append(np.delete(data[:split_idxs[0]],
                                   np.where(data[:split_idxs[0]]==0)[0]))
        remove_idxs = np.append(remove_idxs, np.where(data[:split_idxs[0]]==0)[0] + start_idx)
        
        for i in np.arange(len(split_idxs[1:-1])/2):
            n = 2*i + 1
            data_list.append(np.delete(data[split_idxs[n]:split_idxs[n+1]],
                                       np.where(data[split_idxs[n]:split_idxs[n+1]]==0)[0]))
            remove_idxs = np.append(remove_idxs, np.where(data[split_idxs[n]:split_idxs[n+1]]==0)[0] + start_idx)
        else:
            data_list.append(np.delete(data[split_idxs[-1]:],
                                       np.where(data[split_idxs[-1]:]==0)[0]))
            remove_idxs = np.append(remove_idxs, np.where(data[split_idxs[-1]:]==0)[0] + start_idx)
    else:
        data_list.append(np.delete(data, np.where(data==0)[0]))
        remove_idxs = np.append(remove_idxs, np.where(data==0)[0] + start_idx)

    return data_list, interval_length, remove_idxs


def merge_pitch_file(filenames):
    data_list = []
    merged_data = []
    
    for filename in filenames:
        data = bufconv.read_float(filename)
        data_list.append(data)

    ## merge
    for i in np.arange(len(data_list[0])):
        count = 0.
        value = 0
        
        for data in data_list:
            if not data[i]==0:
                count += 1
            value += data[i]

        if not count==0:
            value /= count
        else:
            value = 0

        merged_data.append(value)
    merged_data = np.array(merged_data)

    ## split(To trim and remove 0)
    data_list, interval, remove_idxs = split(merged_data)

    ## smoothing
    data_list = np.array(map(lambda n:smoothing(n), data_list))

    merged_data = []
    for i,d in enumerate(data_list):
        merged_data = np.append(merged_data, d)
        if not i==len(data_list)-1:
            zeros = np.zeros(interval[i])
            merged_data = np.append(merged_data, zeros)
    
    return merged_data, remove_idxs
