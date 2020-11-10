import os
import sys
import util
import Parse_ast
import Coverage
import SBFL_Formular as SF
import Variable_sus as vs


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
    print(N_tuple)
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
    return SFL_rank, SFL_sus


def cal_final_rank(VSBFL_rank, SFL_rank, variable_info):
    '''
    计算最终怀疑都列表
    '''
    final_rank = []
    for item in VSBFL_rank:
        variable = item['name']
        cover_line_c = []
        for i in range(len(variable_info)):
            if variable in variable_info[i]:
                cover_line_c.append({
                    'no': i+1,
                    'pos': SFL_rank[i]
                })
        cover_line_c.sort(key=lambda s:(s['pos']))
        for i in cover_line_c:
            try:
                final_rank.index(i['no'])
            except:
                final_rank.append(i['no'])
    # print(final_rank)
    return final_rank

def run_file(file_path, test_dir_path, language):
    '''
    计算程序的最后怀疑度列表
    '''
    SFL_rank, SFL_sus = get_SFL_rank(file_path, test_dir_path, language)
    VSBFL_suspicion, VSBFL_rank = vs.cal_VSBFL_rank(file_path, language)
    variable_list = list(VSBFL_suspicion.keys())
    variable_info = util.collect_variable_info(variable_list, file_path)
    print(variable_info)
    final_rank = cal_final_rank(VSBFL_rank, SFL_rank, variable_info)
    print(final_rank)
    return final_rank


if __name__ == "__main__":

    # file_path = r'test\wa.py'
    # test_dir_path = r'test\TEST_DATA_TCG1'
    # run_file(file_path, test_dir_path, 'py')

    file_path = r'test\wa.cpp'
    test_dir_path = r'test\TEST_DATA_TCG1'
    run_file(file_path, test_dir_path, 'cpp')