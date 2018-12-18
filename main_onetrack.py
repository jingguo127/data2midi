# coding = utf-8
import numpy as np
import pretty_midi
import h5py
import os
from random import randrange
from data_processing import *
from data2note import *

file_name_list= ['generated_0','generated_1','generated_2','generated_3','generated_4','generated_5']
bpm = 120
instru_name = 'Acoustic Grand Piano'
unit_time = bpm_to_unit_time(bpm)

for file_name in file_name_list:
    #这里假定h5中的data是只有一轨的
    data_one_track = read_data('2chanel3_5layers/'+file_name+'.hdf5')

    data_one_track_prep,data_one_track_prep_ch1,data_one_track_prep_ch2, bar_number = one_track_data_prep_b(data_one_track, bar_number=None)

    one_track_on_set(data_one_track_prep, p=0.8)

    start_time_matrix, end_time_matrix, start_idices_matrix, end_idices_matrix, notes_numbers_matrix=\
        data_start_end_matrix(data_one_track_prep, unit_time)

    velocity_matrix = velocity_compute_matrix(start_idices_matrix, bar_number,
                                              beat_pattern=[2, 3, 3], bar_length=32,week_range=[60, 90])

    instru = append_note(start_idices_matrix, velocity_matrix, start_time_matrix,
                         end_time_matrix, notes_numbers_matrix,instru_name)

    midi = pretty_midi.PrettyMIDI()
    midi.instruments.append(instru)
    midi.write('2chanel3_5layers/result/'+file_name+'.mid')