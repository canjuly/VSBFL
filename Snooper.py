# -*- coding: utf-8 -*-
import os
import sys
import re
import Parse_ast
import util
import SBFL_Formular as SF
import pysnooper
import Cpp_sequence as cs

py_snooper_file_name = os.path.join('log', 'snooper.py')
py_variable_sequence_file = os.path.join('log', 'py_variable.log')
temp_output_file = os.path.join('log', 'temp.out')
temp_compile_file = os.path.join('log', 'temp')



if sys.platform == "linux":
    COMLINE_PY_COV = "timeout 5 coverage run %s<%s"
    COMLINE_PY_RUN = "timeout 5 python3 %s <%s >%s "
    COMLINE_CPP_COM = "g++ %s -o %s"
    COMLINE_CPP_RUN = "./%s <%s >%s"
    COMLINE_CPP_COV = "gcov %s"
else:
    COMLINE_PY_COV = "coverage run %s<%s"
    COMLINE_PY_RUN = "python %s <%s >%s "
    COMLINE_CPP_COM = "g++ %s -o %s"
    COMLINE_CPP_RUN = "%s <%s >%s"


def prepare_snooper_file(file_path):
    '''
    准备用于pysnooper的文件
    '''
    lines = util.read_file(file_path)
    for i in range(len(lines)):
        lines[i] = '    ' + lines[i]
    lines.insert(0, 'import pysnooper\n')
    lines.insert(1, 'with pysnooper.snoop(depth=2, output=\'' + py_variable_sequence_file + '\'):\n')
    util.write_file(py_snooper_file_name, lines)


def is_correct(temp_output_file, output_file):
    '''
    判断待测程序输出是否正确
    '''
    temp_output_str = util.read_file_by_str(temp_output_file)
    output_str = util.read_file_by_str(output_file)
    if temp_output_str == output_str:
        return True
    else:
        return False

def run_snooper_file(test_dir_path):
    '''
    运行待测程序，并使用pysnooper
    '''
    res_list = []
    test_files = os.listdir(test_dir_path)
    for i in test_files:
        if ".in" not in i:
            continue
        # if "sample.in" not in i:
        #     continue
        input_file = os.path.join(test_dir_path, i)
        output_file = os.path.join(test_dir_path, i[: -2] + "out")
        
        util.clear_file(py_variable_sequence_file)
        cmd = COMLINE_PY_RUN % (py_snooper_file_name, input_file, temp_output_file)
        try:
            os.system(cmd)
        except:
            print('crashed')
            continue
        res = is_correct(temp_output_file, output_file)
        # print(i, res)
        variable_info = parse_py_snooper()
        # print(variable_info)
        res_list.append({
            'res': res,
            'info': variable_info
        })
        # break
    return res_list

def parse_py_snooper():
    '''
    解析pysnooper的输出
    '''
    variable_info = {}
    lines = util.read_file(py_variable_sequence_file)
    now_index = 1
    for line in lines:
        items = line.split(' ')
        items = list(filter(lambda item: item != '', items))
        # print(items)
        if len(items) <= 3:
            continue
        elif items[1] == 'line':
            now_index = int(items[2])
        elif len(items) >= 5 and items[4].find('<') != -1:
            continue
        elif items[1][0:3] == 'var' and items[2][0:2] != '__':
            variable_name = items[2]
            if variable_name not in variable_info:
                # variable_info[variable_name] = {}
                variable_info[variable_name] = []
            variable_value = items[4].replace('\n', '')         #变量不一定是数字
            # variable_info[variable_name][now_index] = variable_value
            variable_info[variable_name].append(variable_value)
    return variable_info

def get_py_variable_sequence(file_path, test_dir_path):
    '''
    获取py代码变量序列
    '''
    prepare_snooper_file(file_path)
    res_list = run_snooper_file(test_dir_path)
    return res_list

def get_cpp_variable_sequence(file_path, test_dir_path):
    '''
    获取cpp代码变量序列
    '''
    res_list = []
    cs.instrumentation(file_path)
    test_files = os.listdir(test_dir_path)
    for i in test_files:
        if ".in" not in i:
            continue
        # if "sample.in" not in i:
        #     continue
        input_file = os.path.join(test_dir_path, i)
        output_file = os.path.join(test_dir_path, i[: -2] + "out")
        info = cs.get_cpp_variable_sequence(input_file)
        cmd1 = COMLINE_CPP_COM % (file_path, temp_compile_file)
        os.system(cmd1)
        cmd2 = COMLINE_CPP_RUN % (temp_compile_file, input_file, temp_output_file)
        os.system(cmd2)
        res = is_correct(temp_output_file, output_file)
        res_list.append({
            'res': res,
            'info': info
        })
        # break
    # print(res_list)
    return res_list

if __name__ == "__main__":
    
    # file_path = r'..\data\3310\WA_py\518603.py'
    # test_dir_path = r'..\data\3310\TEST_DATA_TCG1'
    # print(get_py_variable_sequence(file_path, test_dir_path))

    
    file_path = r'D:\fault_loc\VSFL-TCG\test\AC_c\ac.c'
    test_dir_path = r'D:\fault_loc\VSFL-TCG\test\TEST_DATA_TCG1'
    print(get_cpp_variable_sequence(file_path, test_dir_path))
    