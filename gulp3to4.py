#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import re
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
            else:
                one_line_gulp_task_list.append(line.rstrip())

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
                        if '/*' in gulp_task_line and '*/' in gulp_task_line:
                            gulp_task_line = re.sub('[\[/*].*[*/\],]\s+', '', gulp_task_line)
                        else:
                            gulp_task_line = gulp_task_line.replace('[', 'gulp.series(')
                            gulp_task_line = gulp_task_line.replace(']', ')')
                    # replace : to - in the gulp.series parameter
                    gulp_task_line = gulp_task_line.replace(':', '_')
                    gulp_task_line = gulp_task_line.replace('-', '_')
                gulp_task.append(gulp_task_line.rstrip())

                # add close bracket and curly bracket
                if gulp_task_line.startswith('});'):
                    gulp_task_list.append(gulp_task)
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

# move functions from gulp_task_list to function_list
gulp_task_list_copy = []
for func in gulp_task_list:
    if func[0].startswith('function'):
        function_list.append(func)
    else:
        gulp_task_list_copy.append(func)
gulp_task_list = gulp_task_list_copy

# move gulp.series tasks after single gulp.task
gulp_task_list_copy = []
last_gulp_task_list = []
for func in gulp_task_list:
    if 'gulp.series' in func[0]:
        last_gulp_task_list.append(func)
    else:
        gulp_task_list_copy.append(func)

# resolve forward references issue
for func in last_gulp_task_list:
    


# append to gulp_task_list
for func in last_gulp_task_list:
    gulp_task_list_copy.append(func)
gulp_task_list = gulp_task_list_copy

# print('\n\n\t\t----- one line gulp task list -----\n')
# pp.pprint(one_line_gulp_task_list)
# print('\n\n\t\t----- gulp task function list -----\n')
# pp.pprint(gulp_task_list)
# print('\n\n\t\t----- variable list -----\n')
# pp.pprint(variable_list)
# print('\n\n\t\t----- function list -----\n')
# pp.pprint(function_list)

# reorganize the functions and write to a new file
nf = open(GULP_4_FILE, "w")
var_line = ''
for variable in variable_list:
    var_line += '    ' + variable + ',\n'
var_line = 'var ' + var_line.lstrip()
# replace last comma as semicolon
last_comma_position = var_line.rfind(',')
var_line = var_line[:last_comma_position] + ';' + var_line[last_comma_position+1:]
for line in var_line:
    nf.write(line)

nf.write('\n')

# print out func from function list
for func in function_list:
    for line in func:
        nf.write(line)
        nf.write('\n')
    nf.write('\n')

for func in gulp_task_list:
    for line in func:
        nf.write(line)
        nf.write('\n')
    nf.write('\n')

# print out gulp.task from fulp task list
for func in one_line_gulp_task_list:
    nf.write(func)
    nf.write('\n')

nf.write('\n')

# last bit
nf.write('module.exports = gulp;')
nf.write('\n')

nf.close()
