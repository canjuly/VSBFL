import os
import sys
import util
import Snooper


def get_sequences(wa_file, ac_file, test_dir_path, language):
    '''
    获取错误程序和正确程序的变量变化序列
    '''
    if language == 'py':
        wa_res = Snooper.get_py_variable_sequence(wa_file, test_dir_path)
        ac_res = Snooper.get_py_variable_sequence(ac_file, test_dir_path)
    elif language == 'cpp' or language == 'c':
        wa_res = Snooper.get_cpp_variable_sequence(wa_file, test_dir_path)
        ac_res = Snooper.get_cpp_variable_sequence(ac_file, test_dir_path)
    else:
        wa_res = []
        ac_res = []
    # print(wa_res)
    # print(ac_res)
    return wa_res, ac_res


def fix_style(variable_list):
    '''
    本来的序列均为字符串，要将其转为实际的类型
    '''
    for i in range(len(variable_list)):
        if variable_list[i].find('\'') != -1:         #是否为字符串
            variable_list[i] = variable_list[i].replace('\'', '')
        elif variable_list[i].isdigit():              #是否为整数
            variable_list[i] = int(variable_list[i])
        elif variable_list[i].isdecimal():            #是否为浮点数
            variable_list[i] = float(variable_list[i])
    return variable_list


def add_weight(wa_res, ac_res):
    '''
    计算错误代码中的变量和正确代码变量的边权重
    '''
    weight = {}
    for i in range(len(wa_res)):
        wa_item = wa_res[i]
        ac_item = ac_res[i]
        res = wa_item['res']
        if res == True:
            continue
        wa_info = wa_item['info']
        ac_info = ac_item['info']
        # wa_vars = list(wa_info.keys())
        # ac_vars = list(ac_info.keys())
        for wa_vars in wa_info:
            wa_list = wa_info[wa_vars]
            if wa_vars not in weight:
                weight[wa_vars] = {}
            
            for ac_vars in ac_info:
                ac_list = ac_info[ac_vars]
                LCS = util.cal_LCS(wa_list, ac_list)
                if ac_vars not in weight[wa_vars]:
                    weight[wa_vars][ac_vars] = LCS
                else:
                    weight[wa_vars][ac_vars] += LCS
        # break
    # print(weight)
    return weight


def cal_suspicion(weight, wa_res, ac_res):
    '''
    计算错误代码中各变量的怀疑度值
    '''
    vars_pair = util.cal_KM(weight) #二分图最大完备匹配
    # print(vars_pair)
    vars_len = {}
    for i in range(len(wa_res)):
        wa_item = wa_res[i]
        ac_item = ac_res[i]
        res = wa_item['res']
        if res == True:
            continue
        wa_info = wa_item['info']
        ac_info = ac_item['info']
        for var in vars_pair:
            # vars_len[var] = len(wa_info[var]) + len(ac_info[vars_pair[var]['var']])
            if var not in vars_len:
                vars_len[var] = 0
            if var in wa_info:
                vars_len[var] += len(wa_info[var])
            if vars_pair[var]['var'] in ac_info:
                vars_len[var] += len(ac_info[vars_pair[var]['var']])
    res = {}
    for var in vars_len:
        res[var] = 1 - vars_pair[var]['value'] / (vars_len[var] / 2)
    # print(res)

    return res

def cal_VSBFL_rank(wa_file, ac_file, test_dir_path, language):
    '''
    根据计算变量怀疑度排名
    '''
    wa_res, ac_res = get_sequences(wa_file, ac_file, test_dir_path, language)
    weight = add_weight(wa_res, ac_res)
    VSBFL_suspicion = cal_suspicion(weight, wa_res, ac_res)
    VSBFL_rank = []
    for variable in VSBFL_suspicion:
        VSBFL_rank.append({
            'name': variable,
            'value': VSBFL_suspicion[variable]
        })
    VSBFL_rank.sort(key=lambda s:(s['value']), reverse=True)
    # print(VSBFL_rank)
    return VSBFL_suspicion, VSBFL_rank


if __name__ == "__main__":
    
    cal_VSBFL_rank(r'test\wa.cpp', r'test\ac.cpp', r'test\TEST_DATA_TCG1', 'cpp')
    
