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

def prepare_matrix(file_dir_path, test_dir_path):
    '''
    准备矩阵
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
        if cnt == 2:
            break
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
            # 这种距离的计算方法是否过于草率？
            sum = 0
            for var in vars_pair:
                sum += vars_pair[var]['value']
            dis_matrix[i].append(sum)
            dis_matrix[j].append(sum)
            maxn = max(maxn, sum)
    for i in range(variable_info_list_length):
        for j in range(variable_info_list_length):
            if i != j:
                dis_matrix[i][j] = maxn - dis_matrix[i][j] + 1
    print(dis_matrix)
    return dis_matrix

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
    dis_matrix = prepare_matrix(file_dir_path, test_dir_path)
    arr = np.array(dis_matrix)
    r, c = arr.shape
    num_clusters, indices = hierarchy_cluster(arr)

    print("%d clusters" % num_clusters)
    for k, ind in enumerate(indices):
        print("cluster", k + 1, "is", ind)