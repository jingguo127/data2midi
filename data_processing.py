# coding = utf-8
import numpy as np
import h5py
import os
from random import random

def read_data(file_name, origin=False):
    # 从h5中拿到数据，h5文件要放置在当前文件夹中
    f = h5py.File(os.getcwd() + '/' + file_name, 'r')

    if origin == False:
        data = np.array(f['data'])
    else:
        data=[]
        for k in f:
            print(k)
            if '_' in k or 'label' in k:
                pass
            else:
                x = np.array(f[k])
                data.append(x)
    return data

def one_track_data_prep_a(data_one_track, bar_number=None):
    '''
    针对a方案（单通道，第129行表示头音位置）的处理方案
    data_one_track:单轨data
    bar_number:指定要这轨data的前多少个小节，不填的话，就默认取全部小节
    '''
    # 如果没指定小节数，默认处理数据所有的小节
    if not bar_number:
        bar_number = len(data_one_track)
    # 取我们想要的前N个小节
    data_one_track_prep = data_one_track[:bar_number]

    # （小节数，音高，单小节时值）--->（音高，全曲时值）
    data_one_track_prep = np.concatenate(tuple(data_one_track_prep), axis=1)

    # 对于除了第129行的每一行，根据第129行中的头音位置，将头音数字设置成行数（也就是音高数）
    for i in range(len(data_one_track_prep))[:-1]:
        data_one_track_prep[i] = np.array([i if data_one_track_prep[i][n] == data_one_track_prep[-1][n] else 0 for n in range(len(data_one_track_prep[i]))])

    # 取出第129行
    onset_one_track = data_one_track_prep[-1].astype(np.int64)
    # 干掉第129行
    data_one_track_prep = data_one_track_prep[:-1].astype(np.int64)

    return data_one_track_prep,bar_number, onset_one_track

def one_track_data_prep_b(data_one_track, bar_number=None):
    '''
     针对b方案（双通道，分别表示音位和头音位）的处理方案
     data_one_track:单轨data
     bar_number:指定要这轨data的前多少个小节，不填的话，就默认取全部小节
     '''
    # 如果没指定小节数，默认处理数据所有的小节
    if not bar_number:
        bar_number = len(data_one_track)
    # 取我们想要的前N个小节
    data_one_track_prep = data_one_track[:bar_number].astype(np.int64)

    #(小节数，通道，音高，单小节时值)--->（通道，音高，全曲时值）
    data_one_track_prep = np.concatenate(tuple(data_one_track_prep), axis=2)

    #把两个通道的单独取出，维度变成(音高，全曲时值)
    data_one_track_prep_ch1 = data_one_track_prep[0]
    data_one_track_prep_ch2 = data_one_track_prep[1]

    #把两个通道相加，既是头音又是延音为2，是头不是延或是延不是头都为1，都不是为0，形成这样的新数据
    data_one_track_prep = data_one_track_prep_ch1+data_one_track_prep_ch2

    #把值为2的地方的值改为音高数，也就是行数
    for i in range(len(data_one_track_prep)):
        data_one_track_prep[i] = [i if data_one_track_prep[i][j] == 2 else data_one_track_prep[i][j]
                                  for j in range(len(data_one_track_prep[i]))]

    return data_one_track_prep, data_one_track_prep_ch1,data_one_track_prep_ch2,bar_number

def one_track_data_prep_c(data_one_track, bar_number=None):
    '''
     针对c方案（单通道，128行，2代表头音，1代表延音，0代表没有）的处理方案
     data_one_track:单轨data
     bar_number:指定要这轨data的前多少个小节，不填的话，就默认取全部小节
     '''
    # 如果没指定小节数，默认处理数据所有的小节
    if not bar_number:
        bar_number = len(data_one_track)

    data_one_track = data_one_track*2
    # 取我们想要的前N个小节
    data_one_track_prep = data_one_track[:bar_number].astype(np.int64)

    #(小节数，通道，音高，单小节时值)--->（通道，音高，全曲时值）
    data_one_track_prep = np.concatenate(tuple(data_one_track_prep), axis=1)

    #把值为2的地方的值改为音高数，也就是行数
    for i in range(len(data_one_track_prep)):
        data_one_track_prep[i] = [i if data_one_track_prep[i][j] == 2 else data_one_track_prep[i][j]
                                  for j in range(len(data_one_track_prep[i]))]

    return data_one_track_prep, bar_number

def one_track_concat(data_one_track_prep, onset_one_track, p=0.15):
    '''随机将左右都是延音的头音改成延音，比较适合方案a'''
    #对于onset列表的每一个index
    for j in range(len(onset_one_track)):
        #用这个index找到data_one_track当中的这一列，并对列中的每个音进行操作
        for i in range(len(data_one_track_prep[:,j])):
            #到这里时，i是行的index，j是列的index
            #如果第i行第j列的数据等于行数，也就代表其为头音；j>0是为了保证后面的[j-1]不出bug；头音左右都是1且符合一定概率
            if data_one_track_prep[i][j] == i and j>0 and j<len(data_one_track_prep[i])-1 and data_one_track_prep[i][j-1] == 1 and data_one_track_prep[i][j+1] ==1 and random()<=p:
                #则把头音改成延音
                data_one_track_prep[i][j] = 1

def one_track_on_set(data_one_track_prep, p=0.8):
    '''随机将没有头音而连续2个以上连音的音符加上头音，比较适合方案b'''
    for i in range(len(data_one_track_prep)):
        for j in range(len(data_one_track_prep[i])):
            if data_one_track_prep[i][j] == 1 and j>0 and j<len(data_one_track_prep[i])-1 and data_one_track_prep[i][j-1] == 0 and data_one_track_prep[i][j+1] == 1 and random()<=p:
                data_one_track_prep[i][j] == i





