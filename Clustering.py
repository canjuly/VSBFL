import os
import Snooper
import util
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from matplotlib import pyplot as plt
 
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
    for i in range(len(res1)):
        item1 = res1[i]
        item2 = res2[i]
        info1 = item1['info']
        info2 = item2['info']
        # wa_vars = list(wa_info.keys())
        # ac_vars = list(ac_info.keys())
        for vars1 in info1:
            list1 = info1[vars1]
            if vars1 not in weight:
                weight[vars1] = {}
            
            for vars2 in info2:
                list2 = info2[vars2]
                LCS = util.cal_LCS(list1, list2)
                if vars2 not in weight[vars1]:
                    weight[vars1][vars2] = LCS
                else:
                    weight[vars1][vars2] += LCS
        # break
    # print(weight)
    return weight

def cal_variable_sequence_length(variable_info_list):
    '''
    计算各变量在每个测试样例下的序列长度之和
    '''
    res_list = []
    for item in variable_info_list:
        tmp_dic = {}
        for i in item:
            variable_info = i['info']
            for var in variable_info:
                # vars_len[var] = len(wa_info[var]) + len(ac_info[vars_pair[var]['var']])
                if var not in tmp_dic:
                    tmp_dic[var] = len(variable_info[var])
                else:
                    tmp_dic[var] += len(variable_info[var])
        res_list.append(tmp_dic)
    return res_list

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
    variable_sequence_length = cal_variable_sequence_length(variable_info_list)
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

if __name__ == '__main__':
    
    # arr = [[0., 21.6, 22.6, 63.9, 65.1, 17.7, 99.2],
    # [21.6, 0., 1., 42.3, 43.5, 3.9, 77.6],
    # [22.6, 1., 0, 41.3, 42.5, 4.9, 76.6],
    # [63.9, 42.3, 41.3, 0., 1.2, 46.2, 35.3],
    # [65.1, 43.5, 42.5, 1.2, 0., 47.4, 34.1],
    # [17.7, 3.9, 4.9, 46.2, 47.4, 0, 81.5],
    # [99.2, 77.6, 76.6, 35.3, 34.1, 81.5, 0.]]
    

    file_dir_path = r'E:\fault_loc\data\3955\AC_py'
    test_dir_path = r'E:\fault_loc\data\3955\TEST_DATA_TCG1'
    dis_matrix, file_list = prepare_matrix(file_dir_path, test_dir_path)
    arr = np.array(dis_matrix)
    r, c = arr.shape
    num_clusters, indices = hierarchy_cluster(arr)
    for i in range(len(indices)):
        indices[i] = list(map(lambda num: file_list[num], indices[i]))
    print("%d clusters" % num_clusters)
    for k, ind in enumerate(indices):
        print("cluster", k + 1, "is", ind)