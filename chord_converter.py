# coding = utf-8
import const
import numpy as np
import pretty_midi
import operator

class Chord_Converter():

    def __init__(self,chor_li):
        self.chor_li = chor_li
        '''
        chor_li: [C#MS,D_ms...]和弦表示分4位，分别为：根音(C,D...)、升号(#,_)、性质(M,m,d)、七音(S,s,_)
        :return: 获得一个rang list，里面放着每个和弦范围的range，例：[c,c,c,c,d,d,e,e]为[[0,4],[4,6],[6,8]]
        注意：这里的range是以index为尺度的，还不涉及到时间
        '''
        chor_range_li = []
        i = 0
        while i < len(self.chor_li) - 1:
            range_start = i
            while i < len(self.chor_li) - 1 and self.chor_li[i + 1] == self.chor_li[i]:
                i = i + 1
            i = i + 1
            range_end = i
            chor_range_li.append([range_start, range_end])
        self.chor_range_li = np.array(chor_range_li)

    def __get_chor_range_data_onetrack(self, data_one_track):
        '''
        根据chor_range_li将data_one_track切分成[(128,range1),(128,range2),(128,range3)]
        并获得音符时值累加[(128,),(128,),(128,)]
        data_one_track:[128,全曲长度]
        :return::一轨数据各个和弦范围的数据切片(和弦范围数，128, 和弦范围离散长度)，一轨数据各个和弦范围的音高累计时长表（和弦范围数，128）
        '''
        #chord range data one track
        chor_r_d_onet = []

        #chord range note time one track: 每个和弦范围，一个长度为128的list，代表该和弦范围0-127音高的时值累计 （和弦范围，128）
        chor_r_nt_onet= []

        s = data_one_track.T
        for e in self.chor_range_li:
            chor_r_d_onet.append(s[e[0]:e[1]].T)

        for e in chor_r_d_onet:
            #将数据里的大于0的数字都变成1
            ee = (e>0).astype(np.int64)
            chor_r_nt_onet.append(np.sum(ee,axis=1))

        return np.array(chor_r_d_onet),np.array(chor_r_nt_onet)

    def __get_data_chor_third(self, chor_r_nt_allt):
        '''
        计算数据各和弦范围的三和弦名
        :param chor_r_nt_allt: chord range note time all track,所有轨累加的每个和弦范围各音高的时值,（和弦范围，128）
        :return: data_chor_third: ['C_M', 'C_m','C_d',...]
        '''
        # {'C_M': [], 'C_m': []}
        chor_third_dic = const.CHOR_THIRD_DIC

        data_chor_third = []

        for d in chor_r_nt_allt:
            temp_dict = {}
            for chorname, choridx in chor_third_dic.items():
                #temp_dict: {'C_M':23,'D#m':25} key是和弦名，value是和弦内音累计总时值
                temp_dict[chorname] = np.sum(d[choridx])
                #找到字典中值最大的key,这里代表
                chor = max(temp_dict.items(), key=operator.itemgetter(1))[0]
                data_chor_third.append(chor)
        return data_chor_third

    def __get_data_chor_plus(self, data_chor_third, chor_r_nt_allt):
        '''
        计算数据各和弦范围的附加和弦buff
        :param data_chor_third:['C_M', 'C#m','C_d',...]
        :param chor_r_nt_allt:chord range note time all track,所有轨累加的每个和弦范围各音高的时值,（和弦范围，128）
        :param chor_plus_dict: {'S':11,'s':10}
        :return:data_chor_plus: ['S','s','_'...]
        '''
        base_dic = const.BASE_DIC
        chor_plus_dic = const.CHOR_PLUS_DIC
        data_plus_dic = {}
        data_chor_plus = []

        #从['C_m','D#m',...]中拿出['C_','D#'...]根音名
        data_base = [s[0:2] for s in data_chor_third]

        #将['C_','D#'...]变成[[0,12,24...],[3,15,27...]]音高序列的列表
        data_base_num = np.array([base_dic[n] for n in data_base])


        #对于plus音的各种情况（'s'和'S'两种），k是'S'/'s'，v是11/10
        for k,v in chor_plus_dic.items():

            # {'S':[[0,12,24...]+11,[1,13,25]+10, ....],'s':[[],[],[]...]}
            data_plus_dic[k] = []

            #对于每个和弦范围的根音
            for base in data_base_num:
                #对于和弦范围每个base_list,增加plus音程v，变成plus音高list
                temp_list = base + v

                #如果plus音的indices序列（也就是音高list）第一个音高大于等于12，说明最后一个会大于127，那整体移低1个八度
                if temp_list[0] >= 12:
                    temp_list  = temp_list - 12

                # data_plus_dic {'S':[[每和弦范围S七音indices],[],[]],'s':[[],[],[]]}
                data_plus_dic[k].append(temp_list)

        for i in range(len(chor_r_nt_allt)):
            this_plus_value_dic = {}
            for k,v in data_plus_dic.items():

                #该和弦范围该plus的音高列表
                plus_note_id = data_plus_dic[k][i]

                #该和弦范围内各个音高的累计时值列表
                this_chor_r_nt = chor_r_nt_allt[i]

                #this_chor_r_nt[plus_note_id]算出plus音高的时值列表，sum后变成该范围该plus的总时值
                this_plus_value_dic[k]=np.sum(this_chor_r_nt[plus_note_id])
            #this_plus_value_dic: {'s':28,'S':27}

            #找到this_plus_value_dic中值最大的key
            win_plus_k = max(this_plus_value_dic.items(), key=operator.itemgetter(1))[0]
            if this_plus_value_dic[win_plus_k] >= const.PLUS_THRESHOLD:
                data_chor_plus.append(win_plus_k)
            else:
                data_chor_plus.append('_')
        return data_chor_plus

    def get_data_chor(self, data_all_track):

        chor_r_nt_allt = 0
        for data_one_track in data_all_track:
            chor_r_d_onet, chor_r_nt_onet = self.__get_chor_range_data_onetrack(data_one_track)
            chor_r_nt_allt = chor_r_nt_allt + chor_r_nt_onet
        data_chor_third = self.__get_data_chor_third(chor_r_nt_allt)
        data_chor_plus = self.__get_data_chor_plus(data_chor_third, chor_r_nt_allt)
        data_chor_final = [x[0]+x[1] for x in zip(data_chor_third, data_chor_plus)]

        return data_chor_third, data_chor_plus, data_chor_final

    def convert_data_chor(self, data_all_track, data_chor_final, conv_trac_num=[0,1,4.5,6,7,8,9,10,11,12,13,14,15,16,17,18]):
        '''

        :param data_all_track:
        :param data_chor_third:
        :param data_chor_plus:
        :param data_chor_final:
        :return:不返回，运行的结果就是修改data_all_track
        '''
        # converted_data = []
        base_dic = const.BASE_DIC
        third_note_dic = const.THIRD_NOTE_DIC
        fifth_note_dic = const.FIFTH_NOTE_DIC
        seventh_note_dic = const.SEVENTH_NOTE_DIC

        # 根据 原和弦 和 给的和弦 列表
        # 计算每个范围的数据
        # 1、三音转化 （大-小，小-大）
        # 2、五音转化 （大-d，d-大，小-d，d-小）
        # 2、七音转化（S-s, s-S, S-无，无-S，s-无，无-s）
        # 3、根音转化
        chor_t_li = []
        chor_o_li = []

        for i in range(len(self.chor_li)):
            chor_o = data_chor_final[i]
            chor_t = self.chor_li[i]
            base_o = chor_o[:2]
            base_t = chor_t[:2]
            base_o_num = np.array(base_dic[base_o])
            base_t_num = np.array(base_dic[base_t])
            third_o = third_note_dic[chor_o[2]]
            third_t = third_note_dic[chor_t[2]]
            fifth_o = fifth_note_dic[chor_o[2]]
            fifth_t = fifth_note_dic[chor_t[2]]
            # seventh_o = seventh_note_dic[chor_o[3]]
            # seventh_t = seventh_note_dic[chor_t[3]]
            third_o_num = base_o_num+third_o
            #比如B和弦的3音是D，如果按照B的音高list加三音音程，需要统一降低一个八度
            if third_o_num[0] >= 12:
                third_o_num  = third_o_num -12
            fifth_o_num = base_o_num+fifth_o
            if fifth_o_num[0] >= 12:
                fifth_o_num = fifth_o_num - 12


            #算出目标和弦与原本和弦的根音距离
            base_dist = (base_t_num[0] - base_o_num[0])%12

            #将上述距离转化为音高最近的距离，比如C到F#距离为6，C到G的距离则为-5
            if abs(base_dist) > 6:
                b = 12-abs(base_dist)
                if base_dist >0:
                    base_dist = -b
                else:
                    base_dist = b

            #计算目标和弦与原本和弦的三音、五音、七音与根音音程之间的区别
            third_dist = third_t - third_o
            fifth_dist = fifth_t - fifth_o
            # seventh_dist = seventh_t - seventh_o

            # #目标和弦与原本和弦的七音音程之差可能大于6，比如11与0的差为11，
            # if abs(seventh_dist) >= 6:
            #     b = 12-abs(seventh_dist)
            #     if seventh_dist >0:
            #         seventh_dist = -b
            #     else:
            #         seventh_dist = b

            #根据该和弦范围，切分该范围的各轨数据
            data_all_track_thischor = data_all_track[:,self.chor_range_li[i][0]:self.chor_range_li[i][1]]

            # 针对选定轨的每轨数据,修改三音、五音，再根据根音距离修改所有音高
            for tr_id in conv_trac_num:
                data_one_track_thischor = data_all_track_thischor[tr_id]

                #修改三音音高
                for i in range(len(data_one_track_thischor[third_o_num])):
                    row = data_one_track_thischor[third_o_num][i]
                    #修改三音头音音高
                    row = [x+third_dist if x>1 and x<=127 else x for x in row]
                    #把超过0-127范围的音高数值改回去
                    row = [x+12 if x<0 else x for x in row]
                    row = [x-12 if x>127 else x for x in row]
                    data_one_track_thischor[third_o_num][i]=row

                #修改五音音高
                for i in range(len(data_one_track_thischor[fifth_o_num])):
                    row = data_one_track_thischor[fifth_o_num][i]
                    #修改五音头音音高
                    row = [x+fifth_dist if x>1 and x<=127 else x for x in row]
                    row = [x+12 if x<0 else x for x in row]
                    row = [x-12 if x>127 else x for x in row]
                    data_one_track_thischor[fifth_o_num][i]=row

                #根据根音距离修改所有音高
                for i in range(len(data_one_track_thischor)):
                    row = data_one_track_thischor[i]
                    row = [x+base_dist if x>1 and x<=127 else x for x in row]
                    row = [x+12 if x<0 else x for x in row]
                    row = [x-12 if x>127 else x for x in row]
                    data_one_track_thischor[i]=row

                data_all_track_thischor[tr_id]=data_one_track_thischor

            data_all_track[:, self.chor_range_li[i][0]:self.chor_range_li[i][1]] = data_all_track_thischor









