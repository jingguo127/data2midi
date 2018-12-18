# coding = utf-8

import numpy as np
import pretty_midi
import operator


def get_chor_range(chor_li):
    '''
    获得一个以rang list，里面放着每个和弦范围的range，例：[c,c,c,c,d,d,e,e]为[[0,4],[4,6],[6,8]]
    注意：这里的range是以index为尺度的，还不涉及到时间
    '''
    chor_range_li = []
    i = 0
    while i < len(chor_li) - 1:
        range_start = i
        while i < len(chor_li) - 1 and chor_li[i + 1] == chor_li[i]:
            i = i + 1
        i = i + 1
        range_end = i
        chor_range_li.append([range_start, range_end])

    return np.array(chor_range_li)

def get_chor_range_data_onetrack(chor_range_li, data_one_track):
    '''
    根据chor_range_li将data_one_track切分成[(128,range1),(128,range2),(128,range3)]
    并获得音符时值累加[(128,),(128,),(128,)]
    '''
    #chord range data one track
    chor_r_d_onet = []

    #chord range note time one track: 每个和弦范围，一个长度为128的list，代表该和弦范围0-127音高的时值累计 （和弦范围，128）
    chor_r_nt_onet= []

    s = data_one_track.T
    for e in chor_range_li:
        chor_r_d_onet.append(s[e[0]:e[1]].T)

    for e in chor_r_d_onet:
        #将数据里的大于0的数字都变成1
        ee = (e>0).astype(np.int64)
        chor_r_nt_onet.append(np.sum(ee,axis=1))

    return np.array(chor_r_d_onet),np.array(chor_r_nt_onet)

def get_data_chor_third(chor_r_nt_allt):
    '''
    计算数据各和弦范围的三和弦名
    :param chor_r_nt_allt: chord range note time all track,所有轨累加的每个和弦范围各音高的时值,（和弦范围，128）
    :return: data_chor_third: ['C', 'Cm'...]
    '''
    chor_third_dic = {'C':[],'Cm':[]}
    data_chor_third = []

    for d in chor_r_nt_allt:
        temp_dict = {}
        for chorname, choridx in chor_third_dic.items():

            #temp_dict: {'C':23,'D':25} key是和弦名，value是和弦内音累计总时值
            temp_dict[chorname] = np.sum(d[choridx])

            #找到字典中值最大的key,这里代表
            chor = max(temp_dict.items(), key=operator.itemgetter(1))[0]

            data_chor_third.append(chor)

    return np.array(data_chor_third)

def get_data_chor_plus(data_chor_third, chor_r_nt_onet_alltrack, chor_plus_dict):
    '''
    计算数据各和弦范围的附加和弦buff
    :param data_chor_third:
    :param chor_r_nt_onet_alltrack:
    :param chor_plus_dict: {'7M':7,'7m':6}
    :return:
    '''
    base_dic = {'C':[],'C#':[]...}

    #从['Cm','D#m',...]中拿出['C','D#'...]根音名
    base = [s[0:2] if '#' in s else s[0] for s in data_chor_third]

    #将['C','D#'...]变成[[0,12,24...],[3,15,27...]]音高序列的列表
    base_num = [ base_dic[n] for n in base]


