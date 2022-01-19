# -*- coding: utf-8 -*-
import util
import numpy as np
import Parse_ast as pa

def get_VFL_list(file_path, N_tuple):
    '''
    获得VFL怀疑度列表
    '''
    variable_list = pa.get_cpp_variable_name_list(file_path)
    variable_info = util.collect_variable_info(variable_list, file_path)
    # print(variable_list)
    # print(variable_info)
    # print(N_tuple)

    VFL_score = []
    for var in variable_list:
        item = {
            'var': var,
            'pos': 0,
            'cover': []
        }
        for i,sus in enumerate(N_tuple):
            if var in variable_info[i]:
                item['pos'] += sus
                item['cover'].append({
                    'no': i+1,
                    'pos': sus
                })
        VFL_score.append(item)
    VFL_score.sort(key=lambda s:(s['pos']), reverse=True)
    # print(VFL_score)

    final_rank = []
    VSBFL_rank = []
    visit_list = list(np.zeros(len(N_tuple) + 1))
    tmp_list = []
    for i, item in enumerate(VFL_score):
        VSBFL_rank.append({
            'name': item['var'],
            'value': item['pos']
        })
        tmp_list += item['cover']
        if i != len(VFL_score) - 1 and item['pos'] == VFL_score[i+1]['pos']:
            continue
        tmp_list.sort(key=lambda s:(s['pos']), reverse=True)

        # print(tmp_list)
        insert_list = []
        for j, obj in enumerate(tmp_list):
            if j != len(tmp_list) - 1 and obj['pos'] == tmp_list[j+1]['pos']:
                if visit_list[obj['no']] == 0:
                    insert_list.append(obj['no'])
                    visit_list[obj['no']] = 1
            else:
                if len(insert_list) != 0:
                    final_rank.append(insert_list)
                    insert_list = []
    if len(insert_list) > 0:
        final_rank.append(insert_list)
    insert_list = []
    for i, item in enumerate(visit_list):
        if item == 0 and i != 0:
            insert_list.append(i)
    final_rank.append(insert_list)
    print(VSBFL_rank)
    return final_rank, VSBFL_rank