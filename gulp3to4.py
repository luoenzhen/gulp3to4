#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import time
import shutil
import pprint
import ast

pp = pprint.PrettyPrinter(indent=2)

GULP_3_FILE = 'gulpfile.js'
GULP_4_FILE = 'gulpfile4.js'

# backup gulpfile.js
base_filename, file_extension = os.path.splitext(GULP_3_FILE)
BACKUP_FILE = base_filename + '.' + str(int(time.time())) + '.' + file_extension
# print('backup ' + GULP_3_FILE + ' to ' + BACKUP_FILE)
shutil.copy(GULP_3_FILE, BACKUP_FILE)

variable_list = []
one_line_gulp_task_list = []
gulp_task = []
gulp_task_list = []
function_single = []
function_list = []

# read gulpfile.js
with open(GULP_3_FILE, 'r+') as f:
    lines = f.readlines()
    for i in range(0, len(lines)):
        line = lines[i]

        # variable list
        if line.startswith('var '):
            variable = line.split('var ')[1].split(';')[0]
            variable_list.append(variable)

        # one line gulp task function
        if line.startswith('gulp.task') and not line.rstrip().endswith('{'):
            if len(line.split('\',', 1)) > 1 and line.split('\',', 1)[1].lstrip().startswith('['):
                list_string = '\"' + line.split('\',', 1)[1].split(');')[0].lstrip() + '\"'
                new_gulp_task_str = line.split(' ', 1)[0] + ' gulp.series(' + ast.literal_eval(list_string).replace('[', '').replace(']', '') + '));'
                one_line_gulp_task_list.append(new_gulp_task_str)

        # multi line gulp task function
        if line.startswith('gulp.task') and line.rstrip().endswith('{'):
            task_name = line.split('\'', 1)[1].split('\'', 1)[0]
            # print('👏\t line[' + str(i + 1) + '] --- gulp.task [' + task_name + '] ---\n\t')

            # loop to find the end line of the current gulp task funtion
            for j in range(i, len(lines)):
                gulp_task_line = lines[j]

                # convert array to series with parameter
                if 'gulp.task' in gulp_task_line or 'gulp.watch' in gulp_task_line:
                    if '[' in gulp_task_line and ']' in gulp_task_line:
                        gulp_task_line = gulp_task_line.replace('[', 'gulp.series(')
                        gulp_task_line = gulp_task_line.replace(']', ')')
                    else :
                        gulp_task_line = 'function ' + gulp_task_line.split('\'')[1] + '() {'
                        # print(gulp_task_line)

                gulp_task.append(gulp_task_line.rstrip())

                if gulp_task_line.startswith('});'):
                    if 'gulp.series' in gulp_task[0]:
                        gulp_task[-1] = gulp_task_line.replace(')', '))').rstrip()
                    else:
                        gulp_task[-1] = gulp_task_line.replace('});', '}').rstrip()

                    gulp_task_list.append(gulp_task)
                    # need to return promise
                    if 'del' in lines[j-1]:
                        gulp_task[-2] = '    return ' + gulp_task[-2].lstrip()
                    gulp_task = []
                    break

        # function block
        if line.startswith('function') and line.rstrip().endswith('{'):
            for k in range(i, len(lines)):
                function_single.append(lines[k].rstrip())
                if lines[k].startswith('}'):
                    function_list.append(function_single)
                    function_single = []
                    break

f.close()

print('\n\n\t\t----- one line gulp task list -----\n')
pp.pprint(one_line_gulp_task_list)
print('\n\n\t\t----- gulp task function list -----\n')
pp.pprint(gulp_task_list)
print('\n\n\t\t----- variable list -----\n')
pp.pprint(variable_list)
print('\n\n\t\t----- function list -----\n')
pp.pprint(function_list)

# reorganize the functions and write to a new file
nf = open(GULP_4_FILE, "a")
for variable in variable_list:
    var_line = '   ' + variable + ',\n'
