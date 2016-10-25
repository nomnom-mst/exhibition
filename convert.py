#!/Users/suwakyouhei/.pyenv/shims/python
# -*- coding: utf-8 -*-

import struct
import numpy as np


def write_short(filename, arr):
    with open(filename, "wb") as f:
        for value in arr:
            f.write(struct.pack("h", value))

            
def write_float(filename, arr):
    with open(filename, "wb") as f:
        for value in arr:
            f.write(struct.pack("f", value))

            
def read_short(filename):
    results = []
    with open(filename, "rb") as f:
        while True:
            # 2バイト(SHORT)ずつ読み込む
            b = f.read(2)
            if b == "": break;
            # 読み込んだデータをSHORT型(h)でアンパック
            value = struct.unpack("h", b)[0]
            results.append(value)

    return np.array(results)


def read_float(filename):
    results = []
    with open(filename, "rb") as f:
        while True:
            # 4バイト(FLOAT)ずつ読み込む
            b = f.read(4)
            if b == "": break;
            # 読み込んだデータをFLOAT型(h)でアンパック
            value = struct.unpack("f", b)[0]
            results.append(value)

    return np.array(results)
