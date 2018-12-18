import numpy as np
import pretty_midi

'''
1.建立小节这个类。

'''
class Ref_track():

    def __init__(self, bpm, bar_number, time_sig):
        '''
        :param bpm: int
        :param bar_number: int
        :param time_sig: 长度为2的list，第一个是分母，第二个是分子，比如[4,8]代表8/4拍
        '''
        self.bpm = bpm
        self.bar_number = bar_number
        self.time_sig = time_sig

        # 一拍有多少个32分音符x一小节多少拍x多少小节
        self.length = (32/time_sig[0])*time_sig[1]*bar_number

class Chor_track(Ref_track):

    def __init__(self, bpm, bar_number, time_sig, chor_li):
        '''
        :param bpm: 继承的
        :param bar_number: 继承的
        :param time_sig: 继承的
        :param chor_li: 全曲和弦列表，包含和弦和和弦范围信息
        '''
        super(Chor_track, self).__init__(bpm, bar_number, time_sig)
        self.chor_li = chor_li
        self.chor_rang_li = []


    def get_chor_rang(self):
        '''获得一个以rang list，里面放着每个和弦范围的range，例：[c,c,c,c,d,d,e,e]为[range(0,4),range(4,6),range(6,8)]
        注意：这里的range是以index为尺度的，还不涉及到时间
        '''
        i = 0
        while i < len(self.chor_li) - 1:
            range_start = i
            while i < len(self.chor_li) - 1 and self.chor_li[i + 1] == self.chor_li[i]:
                i = i + 1
            i = i + 1
            range_end = i
            self.chor_rang_li.append(range(range_start, range_end))

    # def chor2num(self,start_idices_matrix, start_time_matrix, end_time_matrix, notes_numbers_matrix):
    #     start_idices_matrix = np.array(start_idices_matrix)
    #     start_time_matrix = np.array(start_time_matrix)
    #     end_time_matrix = np.array(end_time_matrix)
    #     notes_numbers_matrix = np.array(notes_numbers_matrix)
    #     duration_matrix = start_time_matrix-end_time_matrix
    #
    #     for ran in self.chor_rang_li:
    #         for

    def get_notetime_by_chorrang_onetrack(self,start_idices_matrix, start_time_matrix, end_time_matrix, notes_numbers_matrix):
        '''

        :return:
        '''
        start_time_matrix = np.array(start_time_matrix)
        for i in range(len(start_time_matrix)):
            for j in range(len(start_time_matrix[i])):





    def compute_chor_by_rang(self):
        '''
        通过self.chor_rang_li
        :return: 计算出的chorlist，例如[d,d,d,d,e,e,f,f]
        '''
        pass

    def chord_dist(self,ch1,ch2):
        '''

        :return:
        '''

    def conver_dis(self,other_chor_li):
        self.chor_li

        pass

class Chor_single():

    def __init__(self, harmo_dic):
        self.harmo_dic = harmo_dic
    def get_chor_name(self):
        pass
    def

'''
给定和声范围list，算出范围对应的range( range(开始时间，结束时间，单位时间) )
根据start_time_matrix,end_time_matrix,可以算出duration_time_matrix,将stat_time\duration_time\note_number这三个矩阵对应。
对于每个range，算出start_time_matrix当中每个row的哪些start_time在range内。然后把这些

'''