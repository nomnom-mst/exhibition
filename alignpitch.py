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
    for i in np.arange(1, len(zero_idxs[1:])):
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

    interval_idxs_list = filter(lambda n:len(n)>ZERO_LENGTH_THRESH, arrs)
    complement_idxs_list = filter(lambda n:len(n)<=ZERO_LENGTH_THRESH, arrs)
    
    interval_length = map(lambda n:len(n), interval_idxs_list)
    split_idxs = np.array(np.array(map(lambda n:[n[0],n[-1]+1], interval_idxs_list)).flat)

    data_list = []
    if not len(split_idxs)==0:
        complement_idxs = np.array(filter(lambda n: n[0]<split_idxs[0], complement_idxs_list))
        data[:split_idxs[0]] = complement_data(data[:split_idxs[0]], complement_idxs)
        data_list.append(data[:split_idxs[0]])
        
        for i in np.arange(len(split_idxs[1:-1])/2):
            m = 2*i + 1
            complement_idxs = np.array(filter(lambda n:(n[0]<split_idxs[m+1]) and (n[0]>=split_idxs[m]), complement_idxs_list))
            data[split_idxs[m]:split_idxs[m+1]] = complement_data(data[split_idxs[m]:split_idxs[m+1]], complement_idxs, split_idxs[m])
            data_list.append(data[split_idxs[m]:split_idxs[m+1]])
        else:
            complement_idxs = np.array(filter(lambda n: n[0]>=split_idxs[-1], complement_idxs_list))
            data[split_idxs[-1]:] = complement_data(data[split_idxs[-1]:], complement_idxs, split_idxs[-1])
            data_list.append(data[split_idxs[-1]:])
    else:
        data = complement_data(data, complement_idxs_list)
        data_list.append(data)

    return data_list, interval_length, remove_idxs


def complement_data(data, complement_idxs, offset=0):
    for idxs in complement_idxs:
        if len(idxs)==0:
            continue
        idxs = np.array(idxs) - offset
        data[idxs] = np.linspace(data[idxs[0]-1], data[idxs[-1]+1], len(idxs))

    return data


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
