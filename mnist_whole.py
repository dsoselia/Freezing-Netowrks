#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 18:43:53 2018

@author: davitisoselia
"""


import numpy as np
import pandas as pd
from keras.utils  import to_categorical
from sklearn import preprocessing
import keras
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Activation
from keras.optimizers import SGD
from keras.layers import Dense
from keras.layers import Dropout

import numpy as np
from keras import backend as K

from sklearn.utils import class_weight

def index(matrix, a):
    #print(matrix.shape)
    return ([(int(a/matrix.shape[1])), a%int(matrix.shape[1])])

from keras.datasets import mnist

from keras.datasets import mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
    
x_train_lower = [] # corresponding to labels 0-4
y_train_lower = []
x_test_lower = []
y_test_lower = []
    
x_train_upper = [] # corresponding to labels 5-9
y_train_upper = []
x_test_upper = []
y_test_upper = []
    
for i, label in enumerate(y_train):
    x = x_train[i] 
    y = y_train[i]
    if label < 5:  
        x_train_lower.append(x)
        y_train_lower.append(y)
    else:                           
        x_train_upper.append(x)
        y_train_upper.append(y)
                
for i, label in enumerate(y_test):
    x = x_test[i] 
    y = y_test[i]
    if label < 5:  
        x_test_lower.append(x)
        y_test_lower.append(y)
    else:                          
        x_test_upper.append(x)
        y_test_upper.append(y)
        
def train(x , y, x_test, y_test, class_number, model, epochs = 3 ):
    x = np.array(x)
    x_test = np.array(x_test)
    x = x.reshape(x.shape[0], x.shape[1]**2)
    x_test = x_test.reshape(x_test.shape[0], x_test.shape[1]**2)
    x = x.astype('float32')
    x_test = x_test.astype('float32')
    x = x / 255
    x_test = x_test/ 255
    y = to_categorical(np.append(y, 9))[:-1]
    y_test = to_categorical(np.append(y_test, 9))[:-1]

    
    y_ints = [y.argmax() for y in y]
    class_weights = class_weight.compute_class_weight('balanced',
                                                     np.unique(y_ints),
                                                     y_ints)
    model.fit(x,y,epochs = epochs,verbose=1, validation_data = (x_test, y_test))
    
    model.evaluate(x, y)
    model.evaluate(x_test, y_test)
    return model

def evaluate(x,y):
    x = np.array(x)
    x = x.reshape(x.shape[0], x.shape[1]**2)
    x = x.astype('float32')
    x = x / 255
    y = to_categorical(np.append(y, 9))[:-1]
    #print(y[:5])
    print(model.evaluate(x, y))


devisor = 0.5
def get_safe_weights_caller(x,y, model):
    x = np.array(x)
    x = x.reshape(x.shape[0], x.shape[1]**2)
    x = x.astype('float32')
    x = x / 255
    y = to_categorical(np.append(y, 9))[:-1]
    return get_safe_weights(x,y,model)
import keras.backend as k
import tensorflow as tf
def get_safe_weights(x,y,model):
    X=x
    


    outputTensor = model.output #Or model.layers[index].output
    listOfVariableTensors = model.trainable_weights
    gradients = k.gradients(outputTensor, listOfVariableTensors)
    
    trainingExample = x
    sess = tf.InteractiveSession()
    sess.run(tf.initialize_all_variables())
    m = sess.run(gradients,feed_dict={model.input:trainingExample})
    #print([a for a in zip(weights, get_gradients(inputs))])
    #m = [a for a in zip(weights, get_gradients(inputs))]
    annihilated = []
    maxs = []
    for i in range(0,len(m)-1,2):
        maxs.append([])
        min_num = 0
        
        while(min_num<m[i].shape[0]*m[i].shape[1]*devisor):
            max_val = index(m[i], (np.argmax(np.abs(m[i]))))
            m[i][max_val[0]][max_val[1]] = 0
            maxs[-1].append(max_val)
            min_num+=1
            
    
    w = model.get_weights()
    ind  = 0
    for i in range(0,len(m)-1,2):
        #print(ind)
        #print(maxs[ind])
        for max_value in maxs[ind]:
            weight_to_change = [i,max_value[0],max_value[1]]
            w[weight_to_change[0]][weight_to_change[1]][weight_to_change[2]] = 0
            annihilated.append(weight_to_change)
        ind += 1
    return [np.copy(layer) for layer in  w]
#tak = get_safe_weights_caller((x_test_upper), (y_test_upper), model)
'''
model.set_weights(w)
model.evaluate(x_test,y_test)
'''

def overwrite(model,mats):
    values = model.get_weights()
    new_mats=[]
    new_values=[]
    for matrix in mats:
        new_mats.append((matrix==0).astype(int))
    for i in range(len(values)):
        new_values.append((new_mats[i]*values[i])+mats[i])
    #print(values)
    #print(new_values)
    return new_values



model = Sequential()
model.add(Dense(x.shape[1], activation='relu'))
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(10, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy']) 
model = train(x_train_lower, y_train_lower,x_test_lower, y_test_lower , 10, model)
model.save('tes.h5')
safe_weights_stash = get_safe_weights_caller((x_test_lower), (y_test_lower), model)

#print(model.summary())
for i in range(1):
    model = train(x_train_upper, y_train_upper,x_test_upper, y_test_upper ,  10, model, 1)
    new_values = overwrite(model, safe_weights_stash)
    model.set_weights(new_values)

evaluate((x_test_lower), (y_test_lower))
evaluate((x_test_upper), (y_test_upper))
evaluate(x_test,y_test)
<<<<<<< HEAD

import torchvision.models as models
import torch
import torch.nn as nn
import tf_to_pytorch_resnet_152 as kle

model1 = kle.KitModel()
=======
>>>>>>> 4e2907de3e8f671c52cb2fa9ec6dc2d70135082c
