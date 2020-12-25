import openpyxl
import os
import util

def get_tag_info(tag_dir):
    '''
    获取真实的错误信息
    '''
    tag_info = {}
    file_list = os.listdir(tag_dir)
    for i in file_list:
        file_path = os.path.join(tag_dir, i)
        lines = util.read_file(file_path)
        name = lines[0].replace('\n', '')
        num = len(lines[2].split(','))
        if num != 1:
            tag_info[name] = 0
        else:
            tag_info[name] = int(lines[2])
    return tag_info


def cal_top_N(rows, tag_info):
    '''
    统计Top-N的值
    '''
    top_1 = 0
    top_3 = 0
    top_5 = 0
    top_10 = 0
    cnt = 0
    for i, row in enumerate(rows):
        # print(row[0].value, end='\t')
        # print(row[1].value, end='\t')
        # print(row[2].value)
        if i == 0:
            continue
        name = row[0].value
        final_rank = eval(row[1].value)
        if tag_info[name] == 0:
            continue
        cnt += 1
        ans = 0
        for j, column in enumerate(final_rank):
            if tag_info[name] in column:
                ans += 1
                if ans <= 1:
                    top_1 += 1
                if ans <= 3:
                    top_3 += 1
                if ans <= 5:
                    top_5 += 1
                if ans <= 10:
                    top_10 += 1
                break
            else:
                ans += len(column)
        # break
    return top_1/cnt, top_3/cnt, top_5/cnt, top_10/cnt

def cal_exam(rows, tag_info):
    '''
    计算exam值
    '''
    ans = 0
    cnt = 0
    for i, row in enumerate(rows):
        # print(row[0].value, end='\t')
        # print(row[1].value, end='\t')
        # print(row[2].value)
        if i == 0:
            continue
        name = row[0].value
        final_rank = eval(row[1].value)
        if tag_info[name] == 0:
            continue
        cnt += 1
        no = 0
        for j, column in enumerate(final_rank):
            if tag_info[name] in column:
                no += 1
                ans += no
            else:
                no += len(column)
    # print(ans, cnt)
    return ans/cnt

def statistical_fl_results(file_path, tag_dir):
    '''
    统计错误定位的实验结果
    '''
    if file_path.split('.')[-1] != 'xlsx' and file_path.split('.')[-1] != 'xls':
        print('not an execl file')
        return
    wb = openpyxl.load_workbook(file_path) # 读取 工作簿
    ws = wb.worksheets[0]  
    # row_max = ws.max_row # 获取最大行
    # con_max = ws.max_column # 获取最大列
    tag_info = get_tag_info(tag_dir)
    top_1, top_3, top_5, top_10 = cal_top_N(ws.rows, tag_info)
    print(top_1, top_3, top_5, top_10)
    exam = cal_exam(ws.rows, tag_info)
    print(exam)
    return

def cal_exact_result(rows):
    '''
    计算匹配到的代码包含数据集配对代码的数量
    '''
    name = ''
    cnt = 0   #代码份数
    ans1 = 0  #统计结果包含配对代码的
    ans2 = 0  #统计结果恰好是配对代码的
    for i, row in enumerate(rows):
        if i == 0:
            continue
        if row[0].value != None:
            cnt += 1
            name = row[0].value.split('_')[0]
        if row[1].value.find('[') >= 0:
            res_list = eval(row[1].value)
            res_list = list(map(lambda x: x.split('_')[0], res_list))
            # print(res_list)
            if name in res_list:
                ans1 += 1
            if len(res_list) == 1 and res_list[0] == name:
                ans2 += 1
    print(ans1, ans2, cnt)
    return ans1, ans2, ans1/cnt, ans2/cnt

def statistical_parse_results(file_path):
    '''
    统计匹配正确代码的结果
    '''
    if file_path.split('.')[-1] != 'xlsx' and file_path.split('.')[-1] != 'xls':
        print('not an execl file')
        return
    wb = openpyxl.load_workbook(file_path)
    ws = wb.worksheets[0]
    ws.append({'a':'name', 'b':'contain_cnt', 'c':'contain_ratio', 'd':'exact_cnt', 'e':'exact_ratio'})
    for i, sheet in enumerate(wb):
        if i == 0:
            continue
        print(sheet.title)
        ans1, ans2, ratio1, ratio2 = cal_exact_result(sheet.rows)
        ws.append({'a':sheet.title, 'b':ans1, 'c':ratio1, 'd': ans2, 'e': ratio2})
        # break
    wb.save(file_path)
    return

if __name__ == "__main__":
    
    # file_path = r'E:\fault_loc\VSFL-TCG\result\res_2867.xlsx'
    # tag_dir = r'E:\fault_loc\ITSP-data\2867\Tag_c'
    # statistical_fl_results(file_path, tag_dir)

    file_path = r'E:\fault_loc\VSFL-TCG\result\cluster_op2.xlsx'
    statistical_parse_results(file_path)