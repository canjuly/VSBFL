import os
import sys
import Parse_ast
import util
import pyastyle

temp_cpp_file = r'log\temp.cpp'
temp_out_file = r'log\temp.out'

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
    COMLINE_CPP_COV = "gcov %s"

def is_operator(ch):
    '''
    判断是否为特殊字符
    '''
    op_list = '!@#$%^&*()+{}|:\"<>?`-=[]\\;\',./ '
    # print(op_list)
    if op_list.find(ch) != -1:
        return True
    else:
        return False

def find_pos(str1, str2):
    '''
    判断某个字符串中是否含有变量
    '''
    str1_len = len(str1)
    while str2.find(str1) != -1:
        pos = str2.find(str1)
        # print(pos, len(str2))
        if pos == 0 and is_operator(str2[pos + str1_len]):
            return True
        elif pos == len(str2) - str1_len - 1 and is_operator(str2[pos - 1]):
            return True
        elif is_operator(str2[pos - 1]) and is_operator(str2[pos + str1_len]):
            return True
        str2 = str2[pos + str1_len : len(str2)]
    return False


def collect_variable_info(variable_name_list, file_path):
    '''
    收集变量覆盖信息
    '''
    variable_info = []

    lines = util.read_file(file_path)
    for i in range(len(lines)):
        tmp_list = []
        for j in range(len(variable_name_list)):
            if find_pos(variable_name_list[j], lines[i]):
                tmp_list.append(variable_name_list[j])
        variable_info.append(tmp_list)
    return variable_info

def prepare_lines(lines):
    '''
    帮if，while，for后面都加上大括号
    '''
    i = 0
    while i < len(lines):
        if lines[i].find('if') != -1 or lines[i].find('if') != -1 or lines[i].find('while') != -1 or lines[i].find('switch') != -1:
            if lines[i + 1].find('{') < 0:
                lines.insert(i + 1, '{')
                lines.insert(i + 3, '}')
        i += 1
    return lines

def instrumentation(file_name):
    '''
    给源代码插桩
    '''
    variable_list = Parse_ast.get_cpp_variable_name_list(file_name)
    # print(variable_list)
    # variable_info = collect_variable_info(variable_list, file_name)
    # print(variable_info)
    lines = util.read_file(file_name)
    file_type = file_name.split('.')[-1]
    if file_type == 'c':
        lines.insert(0, '#include<iostream>\n')
        for i in range(len(lines)):
            if lines[i].find('#') != -1 and lines[i].find('include') != -1:
                if lines[i].find('.h') != -1:
                    lines[i] = lines[i].replace('<', '<c')
                    lines[i] = lines[i].replace('.h', '')
            else:
                lines.insert(i, 'using namespace std;\n')
                break
    for i in range(len(lines)):
        lines[i] = lines[i].encode('utf-8')
        # lines[i] = lines[i].decode('utf-8')
    util.write_file_by_byte(temp_cpp_file, lines)
    os.system('astyle --style=ansi --add-braces %s' % temp_cpp_file)
    lines = util.read_file(temp_cpp_file)
    # lines = pyastyle.format(lines, '--style=ansi --add-braces').split('\n')
    # lines = prepare_lines(lines)
    # lines = pyastyle.format('\n'.join(lines), '--style=ansi').split('\n')
    # print(lines)
    # return
    i = 0
    while i < len(lines):
        # print(i)
        flag = False
        tmp_str = ''
        # 只有含有等号、输入的语句才会改变变量的值吧
        if lines[i].find('=') >= 0 or find_pos('scanf', lines[i]) or find_pos('cin', lines[i]): 
            for vars in variable_list:
                if find_pos(vars, lines[i]):
                
                    flag = True
                    tmp_str += 'cout << endl << '
                    tmp_str += '"' + vars + ' now is " << ' + vars + ' << endl;'
                    tmp_str += '\n'
       
       
        if flag:
            if lines[i].find('(') >= 0 and lines[i].find(')') >= 0:
                # print('now is: ' + lines[i])
                lines.insert(i + 1, '{')
                lines.insert(i + 2, tmp_str)
                tmp_index = i + 2
                tmp_stack = 0 #用栈记录大括号
                for tmp_index in range(tmp_index + 1, len(lines)):
                    if lines[tmp_index].find('{') >= 0:
                        # print(lines[i], lines[tmp_index])
                        tmp_stack += 1
                    if lines[tmp_index].find('}') >= 0:
                        # print(lines[i], lines[tmp_index])
                        tmp_stack -= 1
                    # print(lines[tmp_index], tmp_stack)
                    if tmp_stack <= 0:
                        break
                # print(lines[tmp_index])
                lines.insert(tmp_index, '}')
                i += 2
                # break
            else:
                lines.insert(i + 1, tmp_str)
                i += 1
                # break
        i += 1
        
    # print(lines)
    for i in range(len(lines)):
        lines[i] = lines[i].encode('utf-8')
    util.write_file_by_byte(temp_cpp_file, lines)
    os.system('astyle --style=ansi %s' % temp_cpp_file)
    return lines

def parse_out(lines):
    '''
    解析插桩程序的输出
    '''
    info = {}
    for line in lines:
        line = line.replace('\n', '')
        items = line.split(' ')
        if len(items) < 4:
            continue
        if items[1] == 'now' and items[2] == 'is':
            variable = items[0]
            st_pos = line.find('is ') + 3
            value = line[st_pos: len(line)]
            if variable not in info:
                info[variable] = []
            else:
                info[variable].append(value)
    return info

def get_cpp_variable_sequence(test_data_file):
    '''
    获取插桩后文件的输出，并提取变量变化序列
    '''
    try:
        execute_file = temp_cpp_file.replace('.cpp', '')
        cmd = COMLINE_CPP_COM % (temp_cpp_file, execute_file)
        os.system(cmd)
        cmd = COMLINE_CPP_RUN % (execute_file, test_data_file, temp_out_file)
        os.system(cmd)
    except expression as identifier:
        print(identifier)
    lines = util.read_file(temp_out_file) # 这里还有问题
    info = parse_out(lines)
    # print(info)
    # data = open(r'..\ViewDemo\public\data\varValue.txt', 'w+')
    # print(info, file=data)
    return info

if __name__ == "__main__":
    
    file_name = r'E:\fault_loc\data\3955\WA_c\515985.c'
    test_data_file = r'E:\fault_loc\data\3955\TEST_DATA_TCG1'
    lines = instrumentation(file_name)
    # info = get_cpp_variable_sequence(test_data_file)
    