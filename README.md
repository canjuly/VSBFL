# VSBFL
> variable sequence based fault localization

## Introduction
* This project corresponds to the experiments and results in the paper `VSBFL: variable sequence based fault localization` (doi links will be added in the future).

* The link of dataset is [here](https://github.com/canjuly/ITSP_data).

## CppSnooper

* Call the function `Snooper.get_cpp_variable_sequence(file_path, test_dir_path)`, and the returned parameter is the corresponding variable value sequences. where `file_path` is the code path and `test_dir_path` is the test case suite path.

## How To Use

* In the file `benmark.py`, call the function `run_dir(file_dir_path, pair_info, test_dir_path)` to start the experiment, note that you need to change the corresponding parameters. 

* parameter `pair_info` is the matching relationship between correct programs and faulty programs, which can be obtained by function `find_pair_by_tag` or `find_pair_by_res`. The difference is that `find_pair_by_tag` is the pairing relationship given by the dataset, while `find_pair_by_res` is the pairing relationship given by the method in this paper.

* The experimental results are saved in the path set by the parameter `res_file_temp`, and this excel file needs to be created by you first.

* If you want to count the experimental results, you can call the `statistical_fl_results(file_path, tag_root_dir)` function in the `statistics.py` file, where `tag_root_dir` is the error message we marked. Before you count the experimental results, please make sure that the first two worksheets in the excel file are blank.

## Result

* The experimental results of this paper are saved in the folder `result`.