# coding = utf-8
import numpy as np
import pretty_midi
from random import randrange

def bpm_to_unit_time(bpm):
    #输入bpm，输出1/32音符的时长
    return 60.0/(bpm*2*4)


def row_start_end_compute(row, unit_time):
    '''
    输入一行数据，计算出这行数据中包含的note对应的
    起始时间、终止时间、音高数字、起始index，终止index的list
    '''
    start_time = []
    end_time = []
    start_idices = []
    end_idices = []
    notes_numbers = []
    for idx in range(len(row)):
        if row[idx] > 1 and row[idx] <= 127:
            start_idx = idx
            end_idx = start_idx
            note_number = row[idx]
            while end_idx < len(row) - 1 and row[end_idx + 1] == 1:
                end_idx = end_idx + 1
            start_idices.append(start_idx)
            end_idices.append(end_idx)
            start_time.append(start_idx * unit_time)
            end_time.append((end_idx + 1) * unit_time)
            notes_numbers.append(note_number)
    return start_time, end_time, start_idices, end_idices, notes_numbers


def data_start_end_matrix(data_one_track_prep, unit_time):
    '''
    逐行使用row_start_end_compute处理数据，
    并返回起始时间、终止时间、音高数字、起始index，终止index的矩阵
    '''
    start_time_matrix = []
    start_idices_matrix = []
    end_time_matrix = []
    end_idices_matrix = []
    notes_numbers_matrix = []
    for row in data_one_track_prep:
        start_time, end_time, start_idices, end_idices, notes_numbers = row_start_end_compute(row, unit_time)

        start_time_matrix.append(start_time)
        end_time_matrix.append(end_time)
        start_idices_matrix.append(start_idices)
        end_idices_matrix.append(end_idices)
        notes_numbers_matrix.append(notes_numbers)
    return start_time_matrix, end_time_matrix, start_idices_matrix, end_idices_matrix, notes_numbers_matrix


def velocity_compute_row(start_idices, beat_pattern, bar_length, week_range, bar_number):
    """
    compute the velocity based on whether the onset of each note is on the heavy or week place;
    return a velocity_list represent the velocity value with respect to every start idex, namely every onset.

    beat_pattern:每个小节的beat分配方式，比如[2,3,3]
    bar_length：每个小节的长度，以数据最小颗粒度为单位，比如数据是以1/32为最小颗粒度，长度为1个整音符，bar_length就是32

    """
    velocity_list = []

    if len(start_idices) == 0:
        return velocity_list
    assert bar_length % sum(beat_pattern) == 0, "beat pattern must match bar_length"
    # print(start_idices[-1], bar_length,bar_number,bar_length*bar_number)
    assert start_idices[-1] < bar_length * bar_number, "start idices must all be smaller then bar_length*bar_number"
    heavy_list = [0]

    #
    beat_length = int(bar_length / sum(beat_pattern))
    beat_pattern_whole = beat_pattern * bar_number
    for beat in beat_pattern_whole:
        heavy_list.append(heavy_list[-1] + beat * beat_length)
    heavy_list = heavy_list[:-1]

    # get a 0 or 1 list which stands for whether each start index is heavy or not
    velocity_list_zero_one = [int(idx in heavy_list) for idx in start_idices]
    for e in velocity_list_zero_one:
        if e == 0:
            velocity_list.append(randrange(week_range[0], week_range[1]))
        else:
            velocity_list.append(100)
    return velocity_list


def velocity_compute_matrix(start_idices_matrix, bar_number, beat_pattern=[2, 3, 3], bar_length=32,
                            week_range=[70, 90]):
    velocity_matrix = []
    for start_idices in start_idices_matrix:
        velocity_matrix.append(velocity_compute_row(start_idices, beat_pattern, bar_length, week_range, bar_number))
    return velocity_matrix


def append_note(start_idices_matrix, velocity_matrix, start_time_matrix, end_time_matrix, notes_numbers_matrix,
                instru_name):
    '''输入data_start_end_matrix函数与velocity_matrix函数返回的信息，输出根据这些信息append好音符的乐器对象instru'''

    # convert instrument name to instrument number
    instru_program = pretty_midi.instrument_name_to_program(instru_name)
    # create instrument instance
    instru = pretty_midi.Instrument(program=instru_program)

    for i in range(len(start_idices_matrix)):
        notes_numbers = notes_numbers_matrix[i]
        velocity_list = velocity_matrix[i]
        start_time = start_time_matrix[i]
        end_time = end_time_matrix[i]

        for idx in range(len(start_time)):
            note = pretty_midi.Note(velocity=velocity_list[idx], pitch=notes_numbers[idx], start=start_time[idx],
                                    end=end_time[idx])
            instru.notes.append(note)

    return instru

