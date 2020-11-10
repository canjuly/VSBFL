def read_file(file_name):
    '''
    已utf-8编码读文件，并按行返回
    '''
    with open(file_name, 'r' ,encoding='utf-8') as f:
        lines = f.readlines()
    return lines

def read_file_by_gbk(file_name):
    '''
    已gbk编码读文件，并按行返回
    '''
    with open(file_name, 'r' ,encoding='gbk') as f:
        lines = f.readlines()
    return lines

def read_file_by_str(file_name):
    '''
    读文件，并按字符串返回
    '''
    with open(file_name, 'r' ,encoding='utf-8') as f:
        str = f.read()
    return str

def write_file(file_name, str):
    '''
    （创建）写文件，从头开始，注意接收参数为列表
    '''
    with open(file_name, 'w+') as f:
        f.writelines(str)

def add_file(file_name, str):
    '''
    （创建）追加文件
    '''
    with open(file_name, 'a+') as f:
        f.writelines(str)

def clear_file(file_name):
    '''
    清空文件
    '''
    with open(file_name, 'r+') as f:
        f.seek(0)
        f.truncate()


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
    判断str2中是否含有变量str1
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

    lines = read_file(file_path)
    for i in range(len(lines)):
        tmp_list = []
        for j in range(len(variable_name_list)):
            if find_pos(variable_name_list[j], lines[i]):
                tmp_list.append(variable_name_list[j])
        variable_info.append(tmp_list)
    return variable_info

def cal_LCS(list1, list2):
    '''
    求最长匹配子串（的长度）
    '''
    ss = []
    l1 = len(list1)
    l2 = len(list2)
    for i in range(l1 + 1):
        temp = []
        for j in range(l2 + 1):
            temp.append(0)
        ss.append(temp)
    for i in range(1, l1 + 1):
        for j in range(1, l2 + 1):
            if list1[i-1] == list2[j-1]:
                ss[i][j] = ss[i-1][j-1] + 1;
                # 如果上一组对应相等，则在上一组所存匹配数加一
            else:
                ss[i][j] = max(ss[i-1][j], ss[i][j-1]);
                # 不相等就取前两种状态匹配数最大值
    return ss[l1][l2]

def cal_KM(weight):
    '''
    二分图匹配
    '''
    from munkres import Munkres, print_matrix, make_cost_matrix
    
    weight_wa_keys = {}
    weight_ac_keys = {}
    matrix = []
    index = 0
    for key in weight:
        weight_wa_keys[index] = key
        index += 1

        row = []
        for i in weight[key]:
            row.append(weight[key][i])
        matrix.append(row)
    index = 0
    for i in weight:
        for j in weight[i]:
            weight_ac_keys[index] = j
            index += 1
        break

    # print_matrix(matrix, msg='matrix:')
    cost_matrix = make_cost_matrix(matrix)
    
    m = Munkres()
    indexes = m.compute(cost_matrix)
    vars_pair = {}
    # print_matrix(matrix, msg='Highest profits through this matrix:')
    # total = 0
    for row, column in indexes:
        value = matrix[row][column]
        vars_pair[weight_wa_keys[row]] = {
            'var': weight_ac_keys[column],
            'value': value
        }
        # total += value
        # print(f'({weight_wa_keys[row]}, {weight_ac_keys[column]}) -> {value}')
    # print(f'total profit={total}')
    # print(vars_pair)
    return vars_pair


if __name__ == "__main__":
    # print(cal_LCS( [2, 4], [1, 2, 3, 4]))
    # weight = {'n': {'n': 78, 'i': 1}, 'i': {'n': 0, 'i': 77}, 'j': {'n': 79, 'i': 80}}
    weight = {'a': {'s1': 8, 's2': 2, 's3': 8, 'i': 0}, 'b': {'s1': 2, 's2': 8, 's3': 5, 'i': 0}, 
    'k': {'s1': 0, 's2': 0, 's3': 0, 'i': 6}, 'List': {'s1': 0, 's2': 0, 's3': 0, 'i': 0}, 'i': {'s1': 0, 's2': 0, 's3': 0, 'i': 3}}
    print(cal_KM(weight))