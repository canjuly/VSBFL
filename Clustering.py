# -*- coding: utf-8 -*-
import os
import Snooper
import util
import numpy as np
import openpyxl
# from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
# from matplotlib import pyplot as plt

cluster_file = r'result\cluster_op2.xlsx'

def get_ac_res(ac_dir, test_dir_path, res_dir):
    '''
    将正确代码的变量变化序列记录下来，以便后期匹配
    '''
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)
    ac_file_list = os.listdir(ac_dir)
    for ac_file in ac_file_list:
        ac_file_path = os.path.join(ac_dir, ac_file)
        file_type = ac_file.split('.')[-1]
        print(ac_file)
        if file_type == 'cpp' or file_type == 'c':
            variable_info = Snooper.get_cpp_variable_sequence(ac_file_path, test_dir_path)
        elif file_type == 'py':
            variable_info = Snooper.get_py_variable_sequence(ac_file_path, test_dir_path)
        print(variable_info)
        res_file = os.path.join(res_dir, ac_file.split('.')[0] + '.out')
        util.write_file(res_file, str(variable_info))
        # break
    return
 
def hierarchy_cluster(data, method='average', threshold=5.0):
    '''层次聚类
    
    Arguments:
        data [[0, float, ...], [float, 0, ...]] -- 文档 i 和文档 j 的距离
    
    Keyword Arguments:
        method {str} -- [linkage的方式： single、complete、average、centroid、median、ward] (default: {'average'})
        threshold {float} -- 聚类簇之间的距离
    Return:
        cluster_number int -- 聚类个数
        cluster [[idx1, idx2,..], [idx3]] -- 每一类下的索引
    '''
    data = np.array(data)
 
    Z = linkage(data, method=method)
    cluster_assignments = fcluster(Z, threshold, criterion='distance')
    # print(type(cluster_assignments))
    num_clusters = cluster_assignments.max()
    indices = get_cluster_indices(cluster_assignments)
 
    return num_clusters, indices
 
def get_cluster_indices(cluster_assignments):
    '''映射每一类至原数据索引
    
    Arguments:
        cluster_assignments 层次聚类后的结果
    
    Returns:
        [[idx1, idx2,..], [idx3]] -- 每一类下的索引
    '''
    n = cluster_assignments.max()
    indices = []
    for cluster_number in range(1, n + 1):
        indices.append(np.where(cluster_assignments == cluster_number)[0])
    
    return indices
 
 
def add_weight(res1, res2):
    '''
    计算错误代码中的变量和正确代码变量的边权重
    '''
    weight = {}
    var_list1 = []
    var_list2 = []
    # print(res1)
    # print(res2)
    for i in range(len(res1)):
        item1 = res1[i]
        item2 = res2[i]
        info1 = item1['info']
        info2 = item2['info']
        for vars1 in info1:
            list1 = info1[vars1]
            if vars1 not in var_list1:
                var_list1.append(vars1)
                weight[vars1] = {}

            for vars2 in info2:
                list2 = info2[vars2]
                if vars2 not in var_list2:
                    var_list2.append(vars2)

                LCS = util.cal_LCS(list1, list2)
                # print(vars1, vars2, LCS)
                if vars2 not in weight[vars1]:
                    weight[vars1][vars2] = LCS
                else:
                    weight[vars1][vars2] += LCS
        # break
    for vars1 in var_list1:
        for vars2 in var_list2:
            if vars2 not in weight[vars1]:
                weight[vars1][vars2] = 0
    # print(weight)
    return weight

def cal_variable_sequence_length(variable_info_list):
    '''
    计算各变量在每个测试样例下的序列长度之和
    '''
    res_dict = {}
    for i in variable_info_list:
        variable_info = i['info']
        for var in variable_info:
            # print(var)
            # vars_len[var] = len(wa_info[var]) + len(ac_info[vars_pair[var]['var']])
            if var not in res_dict:
                res_dict[var] = len(variable_info[var])
            else:
                res_dict[var] += len(variable_info[var])
    # print(res_dict)  
    return res_dict

def prepare_matrix(file_dir_path, test_dir_path):
    '''
    准备矩阵，第二个返回值是文件列表
    '''
    file_list = os.listdir(file_dir_path)
    variable_info_list = []
    cnt = 0
    for i in file_list:
        file_path = os.path.join(file_dir_path, i)
        variable_info = Snooper.get_py_variable_sequence(file_path, test_dir_path)
        variable_info_list.append(variable_info)
        print(variable_info)
        cnt += 1
        if cnt == 15:
            break
    variable_sequence_length = []
    for i in variable_info_list:
        variable_sequence_length.append(cal_variable_sequence_length(i))
    # print(variable_sequence_length)
    variable_info_list_length = len(variable_info_list)
    dis_matrix = []
    maxn = 0
    for i in range(variable_info_list_length):
        dis_matrix.append([])
    for i in range(variable_info_list_length):
        dis_matrix[i].append(0)
        for j in range(i+1, variable_info_list_length):
            weight = add_weight(variable_info_list[i], variable_info_list[j])
            vars_pair = util.cal_KM(weight)
            # print(vars_pair)
            # 距离的计算方法为：
            # 1. 对于每个变量，首先算出他和对应变量的LCS
            # 2. 算出该变量在所有测试样例中的序列长度和len1
            # 3. 算出该变量的对应变量在所有测试样例中的序列长度和len2
            # 4. 这两个变量的距离即为LCS*2/(len1 + len2)
            # 5. 两份代码的距离即为所有变量的距离之和
            # 6. 由于聚类算法距离越近就越容易将两个点划进同一类簇，
            #    故需对上面的得到的距离求反再代入聚类算法
            sum = 0
            for var in vars_pair:
                len1 = variable_sequence_length[i][var]
                var2 = vars_pair[var]['var']
                len2 = variable_sequence_length[j][var2]
                sum += vars_pair[var]['value'] * 2.0 / (len1 + len2)
                # print(var, ' is', str(vars_pair[var]['value'] * 2.0 / (len1 + len2)))
                # sum += vars_pair[var]['value']
            dis_matrix[i].append(sum)
            dis_matrix[j].append(sum)
            maxn = max(maxn, sum)
    for i in range(variable_info_list_length):
        for j in range(variable_info_list_length):
            if i != j:
                dis_matrix[i][j] = maxn - dis_matrix[i][j] + 1 # 加1是人工定义了两份不同的代码距离至少为1
    print(dis_matrix)
    return dis_matrix, file_list


def slice_file_by_cluster(num_clusters, indices):
    '''
    依据分类结果进行文件操作
    '''
    return 

def find_similar_ac_file(wa_res, ac_res_dir):
    '''
    寻找和错误代码相似的正确代码
    '''
    wa_variable_length = cal_variable_sequence_length(wa_res)
    ac_file_list = os.listdir(ac_res_dir)
    res_file = []
    res_list = []
    maxn = 0
    for ac_file in ac_file_list:
        ac_file_path = os.path.join(ac_res_dir, ac_file)
        ac_res = eval(util.read_file(ac_file_path)[0])
        ac_variable_length = cal_variable_sequence_length(ac_res)
        # print(ac_file, end='\t')
        # print(ac_res)
        # print(wa_variable_length)
        # print(ac_variable_length)
        weight = add_weight(wa_res, ac_res)
        # print(weight)
        vars_pair = util.cal_KM(weight)
        # print(vars_pair)
        sum = 0
        cnt = 0
        for var in vars_pair:
            cnt += 1
            len1 = wa_variable_length[var]
            var2 = vars_pair[var]['var']
            len2 = ac_variable_length[var2]
            sum += vars_pair[var]['value'] * 2.0 / (len1 + len2)
        # print(sum)
        # sum = sum / cnt  # 另一种计算相似度的方法
        res_list.append({
            'file': ac_file,
            'sum': sum
        })
        if abs(sum - maxn) < 0.001:
            res_file.append(ac_file)
        elif sum > maxn:
            maxn = sum
            res_file = [ac_file]
        # break
    # print(res_file)
    return res_file, res_list

def run_dir(wa_dir, ac_res_dir, test_dir_path):
    '''
    获取某个文件夹内所有文件的匹配的相似正确代码
    '''
    wa_list = os.listdir(wa_dir)
    wb = openpyxl.load_workbook(cluster_file)
    problem_id = wa_dir.split('\\')[-2]
    wb.create_sheet(problem_id)
    ws = wb[problem_id]
    ws.append({'a':'wa_code', 'b':'ac_code', 'c':'similarity'})
    for wa_file in wa_list:
        wa_file_path = os.path.join(wa_dir, wa_file)
        print(wa_file)
        wa_res = Snooper.get_cpp_variable_sequence(wa_file_path, test_dir_path)
        # print(wa_res)
        # return
        res_file, res_list = find_similar_ac_file(wa_res, ac_res_dir)
        print(res_file)
        for i, item in enumerate(res_list):
            if i == 0:
                ws.append({'a':wa_file, 'b':item['file'], 'c':item['sum']})
            else:
                ws.append({'b':item['file'], 'c':item['sum']})
        ws.append({'b':str(res_file)})
    wb.save(cluster_file)
    return 

if __name__ == '__main__':
    
    # arr = [[0., 21.6, 22.6, 63.9, 65.1, 17.7, 99.2],
    # [21.6, 0., 1., 42.3, 43.5, 3.9, 77.6],
    # [22.6, 1., 0, 41.3, 42.5, 4.9, 76.6],
    # [63.9, 42.3, 41.3, 0., 1.2, 46.2, 35.3],
    # [65.1, 43.5, 42.5, 1.2, 0., 47.4, 34.1],
    # [17.7, 3.9, 4.9, 46.2, 47.4, 0, 81.5],
    # [99.2, 77.6, 76.6, 35.3, 34.1, 81.5, 0.]]
    

    # file_dir_path = r'E:\fault_loc\data\3955\AC_py'
    # test_dir_path = r'E:\fault_loc\data\3955\TEST_DATA_TCG1'
    # dis_matrix, file_list = prepare_matrix(file_dir_path, test_dir_path)
    # arr = np.array(dis_matrix)
    # r, c = arr.shape
    # num_clusters, indices = hierarchy_cluster(arr)
    # for i in range(len(indices)):
    #     indices[i] = list(map(lambda num: file_list[num], indices[i]))
    # print("%d clusters" % num_clusters)
    # for k, ind in enumerate(indices):
    #     print("cluster", k + 1, "is", ind)

    problem_list = [2810, 2811, 2812, 2813, 2824, 2825, 2827, 2828, 2830, 2831, 2832, 2833, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871]
    for problem in problem_list:
        # problem = 2866
        print(problem)
        ac_dir = os.path.join(r'D:\fault_loc\ITSP-data', str(problem), 'AC_c')
        test_dir_path = os.path.join(r'D:\fault_loc\ITSP-data', str(problem), 'TEST_DATA_TCG1')
        ac_res_dir = os.path.join(r'D:\fault_loc\ITSP-data', str(problem), 'Res_c')
        wa_dir = os.path.join(r'D:\fault_loc\ITSP-data', str(problem), 'WA_c')
        get_ac_res(ac_dir, test_dir_path, ac_res_dir)
        # run_dir(wa_dir, ac_res_dir, test_dir_path)
        # break
    # res1 = Snooper.get_cpp_variable_sequence(r'E:\fault_loc\ITSP-data\2871\WA_c\278419_buggy.c', r'E:\fault_loc\ITSP-data\2871\TEST_DATA_TCG1')
    # res2 = eval(util.read_file(r'E:\fault_loc\ITSP-data\2871\Res_c\278461_correct.out')[0])
    # print(add_weight(res1, res2))