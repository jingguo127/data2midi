# coding = utf-8

'''
Chor_third_dic
三和弦的命名规则：
第一位：根音音名，C\D\E\F...
第二位：升号，无升号的需要填写补位符号'_', #\_
第三位：和弦大小，m\M
'''
CHOR_THIRD_DIC = {'C_M': [], 'C#m': [],'D_M':[]}

#该和弦附加名对应的附加音偏斜（关于根音）

CHOR_PLUS_DIC = {'S':11,'s':10}

'''
Base_dic
根音音名命名规则：
第一位：根音音名
第二位：升号，无升号的需要填写补位符号'_', #\_
'''
BASE_DIC = {'C_': [], 'C#': []}

PLUS_THRESHOLD = 10

#带m/M/d的和弦分别的三音与根音的音程
THIRD_NOTE_DIC = {'m': 3, 'M':4, 'd':3}

#带m/M/d的和弦分别的五音与根音的音程
FIFTH_NOTE_DIC = {'m': 7, 'M':7, 'd':6}

SEVENTH_NOTE_DIC = {'s': 10, 'S':11, '_': 0}