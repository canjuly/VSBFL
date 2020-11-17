import os
import sys
import util
import Parse_ast
import Coverage
import SBFL_Formular as SF
import Variable_sus as vs

problem_id = 3955
res_file = 'res1.out'

def find_pair(dir_path):
    '''
    寻找每份错误代码对应的正确代码
    '''
    pair_info = {}
    tag_files = os.listdir(dir_path)
    for i in tag_files:
        tag_file = os.path.join(dir_path, i)
        lines = util.read_file(tag_file)
        wa_file = lines[0].replace('\n', '')
        ac_file = lines[1].replace('\n', '')
        pair_info[wa_file] = ac_file
    # for file in pair_info:
    #     print(file, pair_info[file])
    return pair_info

def cal_N_tuple(passed_test_num, failed_test_num, lines_passed,  lines_failed):
    '''
    计算各行的怀疑度值
    这里可以切换相似系数（我不知道我相似系数那几个公式对不对。。）
    '''
    N_tuple = []
    line_num = len(lines_passed)  #其实比实际行数多一行，因为有个第0行
    for i in range(1, line_num):
        Ncf = lines_failed[i]
        Nuf = failed_test_num - lines_failed[i]
        Ncp = lines_passed[i]
        Nup = passed_test_num - lines_passed[i]
        # Tarantula = SF.cal_turantula(Ncf, Nuf, Ncp, Nup)
        Jaccard = SF.cal_jaccard(Ncf, Nuf, Ncp, Nup)
        # Naish = SF.cal_naish(Ncf, Nuf, Ncp, Nup)
        # GP08 = SF.cal_GP08(Ncf, Nuf, Ncp, Nup)
        # GP10 = SF.cal_GP10(Ncf, Nuf, Ncp, Nup)
        # GP11 = SF.cal_GP11(Ncf, Nuf, Ncp, Nup)
        # GP13 = SF.cal_GP13(Ncf, Nuf, Ncp, Nup)
        # GP20 = SF.cal_GP20(Ncf, Nuf, Ncp, Nup)
        # GP26 = SF.cal_GP26(Ncf, Nuf, Ncp, Nup)
        # print(i, Jaccard)
        N_tuple.append(Jaccard)
    return N_tuple  #返回值没有第0行

def get_SFL_rank(file_path, test_dir_path, language):
    '''
    计算SBFL的怀疑度和排名
    '''
    if language == 'py':
        passed_test_num, failed_test_num, lines_passed,  lines_failed = Coverage.get_python_cov_info(file_path, test_dir_path)
    elif language == 'cpp':
        passed_test_num, failed_test_num, lines_passed,  lines_failed = Coverage.get_cpp_cov_info(file_path, test_dir_path)
    else:
        return [], []
    # print(passed_test_num, failed_test_num)
    # print(lines_passed,  lines_failed)
    N_tuple = cal_N_tuple(passed_test_num, failed_test_num, lines_passed,  lines_failed)
    # print(N_tuple)
    N_tuple_c = []
    for i in range(len(N_tuple)):
        N_tuple_c.append({
            'no': i + 1,
            'similarity': N_tuple[i]
        })
    N_tuple_c.sort(key=lambda s:(s['similarity']), reverse=True)
    SFL_rank = []
    SFL_sus = []
    for i in N_tuple_c:
        SFL_rank.append(i['no'])
        SFL_sus.append(i['similarity'])
    # print(SFL_sus)
    return SFL_rank, SFL_sus, N_tuple


def cal_final_rank(VSBFL_rank, SFL_rank, N_tuple, variable_info):
    '''
    计算最终怀疑都列表
    '''
    final_rank = []

    # 新的排序方法
    coefficient_list = []
    final_rank_t = []
    VSBFL_dic = {}
    for item in VSBFL_rank:
        VSBFL_dic[item['name']] = item['value']
    for i in range(len(variable_info)):
        coefficient = 0
        for variable in variable_info[i]:
            coefficient += VSBFL_dic[variable]
        if len(variable_info[i]) != 0:
            coefficient = 1 + coefficient / len(variable_info[i])
        else:
            coefficient = 1.0
        coefficient_list.append(coefficient)
    for i in range(len(N_tuple)):
        final_rank_t.append({
            'no': i + 1,
            'pos': N_tuple[i] * coefficient_list[i]
        })
    final_rank_t.sort(key=lambda s: s['pos'], reverse=True)
    for i in final_rank_t:
        final_rank.append(i['no'])


    # 旧的排序方法
    # for item in VSBFL_rank:
    #     variable = item['name']
    #     cover_line_c = []
    #     for i in range(len(variable_info)):
    #         if variable in variable_info[i]:
    #             cover_line_c.append({
    #                 'no': i+1,
    #                 'pos': SFL_rank[i]
    #             })
    #     cover_line_c.sort(key=lambda s:(s['pos']))
    #     for i in cover_line_c:
    #         try:
    #             final_rank.index(i['no'])
    #         except:
    #             final_rank.append(i['no'])

    # print(final_rank)
    return final_rank

def run_file(file_path, ac_file, test_dir_path, language):
    '''
    计算程序的最后怀疑度列表
    '''
    print(file_path, ac_file)
    SFL_rank, SFL_sus, N_tuple = get_SFL_rank(file_path, test_dir_path, language)
    # print(SFL_rank, SFL_sus, N_tuple)
    VSBFL_suspicion, VSBFL_rank = vs.cal_VSBFL_rank(file_path, ac_file, test_dir_path, language)
    variable_list = list(VSBFL_suspicion.keys())
    variable_info = util.collect_variable_info(variable_list, file_path)
    # print(variable_info)
    final_rank = cal_final_rank(VSBFL_rank, SFL_rank, N_tuple, variable_info)
    print(final_rank)
    return final_rank

def run_dir(file_dir_path, pair_info, test_dir_path):
    '''
    计算某个文件夹内所有文件的最后怀疑度列表
    '''
    file_list = os.listdir(file_dir_path)
    for file in file_list:
        file_type = file.split('.')[-1]
        if file_type == 'c' or file_type == 'cpp' or file_type == 'py':
            wa_file_path = os.path.join(file_dir_path, file)
            ac_file_path = os.path.join(r'E:\fault_loc\data', str(problem_id), 'AC_'+file_type, pair_info[file])
            # print(wa_file_path, ac_file_path)
            try:
                final_rank = run_file(wa_file_path, ac_file_path, test_dir_path, file_type)
                util.add_file(res_file, file + '    ' + str(final_rank) + '\n')
            except:
                util.add_file(res_file, file + '    ' + 'contains error\n')
    return


if __name__ == "__main__":

    pair_info = find_pair(r'E:\fault_loc\data\3955\TAG_py')
    # file_path = r'E:\fault_loc\data\3955\WA_py\508560.py'
    # ac_file = os.path.join(r'E:\fault_loc\data\3955\AC_py', pair_info['508560.py'])
    # test_dir_path = r'E:\fault_loc\data\3955\TEST_DATA_TCG1'
    # run_file(file_path, ac_file, test_dir_path, 'py')

    file_path = r'E:\fault_loc\data\3955\WA_py'
    test_dir_path = r'E:\fault_loc\data\3955\TEST_DATA_TCG1'
    run_dir(file_path, pair_info, test_dir_path)