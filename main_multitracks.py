# coding = utf-8
import numpy as np
import pretty_midi
import h5py
import os
from random import randrange
from data_processing import *
from data2note import *

'''
   0,  '主旋律1'
   1,   '主旋律2'
   2,   '噪音1'
   3,   '噪音2'
   4,   'Distortion Guitar1'
   5,   'Distortion Guitar2'
   6,   'Acoustic Piano1'
   7,  'Acoustic Piano2'
   8,  'Overdriven Guitar'
   9,  'Electric Bass'
   10,  'Acoustic Guitar1'
   11,  'Acoustic Guitar2'
   12,  'Electric Guitar1'
   13,  'Electric Guitar2'
   14,  'String Ensemble 1'
   15,  'String Ensemble 2'
   16,  '点声源'
   17,  '线声源'
   18,  '音效'
'''

file_name_list = ['decoded_22','decoded_18']
bpm = 120
unit_time = bpm_to_unit_time(bpm)

for file_name in file_name_list:

    origin = False
    if 'origin' in file_name:
        origin = True
    data = read_data('multi_track/'+file_name+'.hdf5',origin)

    #临时处理，增加一个维度为了适配下面的代码
    #data = np.array([data])

    for i in range(len(data)):
        data_one_track = data[i]
        if np.sum(data_one_track):
            data_one_track_prep, data_one_track_prep_ch1, data_one_track_prep_ch2, bar_number = one_track_data_prep_b(
                data_one_track, bar_number=None)
            one_track_on_set(data_one_track_prep, p=0.8)
            start_time_matrix, end_time_matrix, start_idices_matrix, end_idices_matrix, notes_numbers_matrix = \
                data_start_end_matrix(data_one_track_prep, unit_time)
            velocity_matrix = velocity_compute_matrix(start_idices_matrix, bar_number,
                                                      beat_pattern=[2,2,2,2], bar_length=32, week_range=[60, 90])
            instru = append_note(start_idices_matrix, velocity_matrix, start_time_matrix,
                                 end_time_matrix, notes_numbers_matrix, 'Cello')
            midi = pretty_midi.PrettyMIDI()
            midi.instruments.append(instru)
            midi.write('multi_track/result/' + file_name +'_track'+str(i)+ '.mid')
