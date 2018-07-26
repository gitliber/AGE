# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 14:25:51 2018

@author: lav solanki
"""
import numpy as np
import h5py
f = h5py.File('models/imdb/imdb.mat', 'r')
data = f.get('data/var1')
data = np.array(data)
