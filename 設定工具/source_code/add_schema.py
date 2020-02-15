#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:30:55 2020

@author: nienpo@yahoo.com
survey the same directory as this script
the existence of *.schema.yaml
and default.custom.yaml

create or modify default.custom.yaml
"""


from os import sep, system
from os.path import exists, abspath
from glob import glob
from datetime import datetime
from sys import platform, argv

in_development = False

###########################################
def remove_comment(a_line, ch="#"):
    '''
    送進一行程式碼
    這個函數要把註解 (# 符號起頭，從行首開始，或從行中開始) 從 此行 裏移除，
    再從右方移除空白 (如果註解移除後只剩下空白，則會全部去除成空字串；不然，回傳的空白
    會誤導這一行是有內縮格子的有意義文字)
    然後回傳。

    Parameters
    ----------
    a_line : str
        一行程式碼
    cr: str
        註解符號, 預設是 "#"

    Returns
    -------
    str
    移除註解後的程式碼

    by npchen, 2020/2/15
    '''

    pt = a_line.find(ch)
    if pt != -1:
        # keep all chars before #
        a_line = a_line[0: pt]
    
    # clean up white spaces from right
    # if there are only spaces after removing the comment
    # this action will result in an null str
    # to avoid returning mis-leading heading spaces
    return a_line.rstrip()
###########################################
def get_leading_space(a_line):
    '''
    送進一行有內縮結構的文字 (以空格個數內縮)
    回傳前面的空白
    '''
    # only stripping from the left (removing all of the leading spaces)
    stripped_line = a_line.lstrip()
    pt = a_line.find(stripped_line[0])
    return a_line[0:pt]
###########################################
def extract_schema_name(a_line):
    '''
    cleaned_line: str
    a non-empty line.  It can be
    "    - schema: k_syh_t_m"
    "    - {schema: k_syh_t_m}"
    return
    the schema name str
    '''
    # locate the ":"
    pt = a_line.find(":")
    
    # extract from the next char to the end
    schema_name = a_line[pt+1: ]
    
    # the right side contains "}" and/or additional spaces
    # remove them
    # new line and space have to be listed explicitly
    schema_name = schema_name.strip(" }\n")
    
    return schema_name
    
###########################################
def get_schema_lst(all_lines_lst):
    '''
    a list contains all lines in a file
    each element is from a line
    return a list of strings (names of schema)
           and an int to indicate the line number of the last schema
    '''
    schema_lst = []
    isWithinBlock = False
    counter = 0
    counter_for_block = 0
    for a_line in all_lines_lst:
        cleaned_line = remove_comment(a_line, "#")
        if cleaned_line.find("schema_list:") !=  -1:
            # this will only happen once
            isWithinBlock = True
            leading_space_count_of_header = len( get_leading_space(cleaned_line) )
        elif isWithinBlock and len(cleaned_line) > 0:
            # a non-empty line within block (after the line of schema_list: )
            leading_space_count = len( get_leading_space(cleaned_line) )
            if leading_space_count == leading_space_count_of_header + 2 \
            and "schema" in cleaned_line :
                # a meaningful schema list entry
                schema_lst.append( extract_schema_name(cleaned_line)  )
                counter_for_block = counter
            elif leading_space_count == leading_space_count_of_header:
                # the block ends
                # no need to scan further
                isWithinBlock = False
                break
                
        counter += 1
    
         
    # all lines have been scanned
    # if there's no such block in all_lines_lst
    # schema_lst will be empty,
    # counter_for_block will be zero
    # returning empty list and 1
    # 
    return schema_lst, counter_for_block + 1
###########################################
def make_template_str(a_line):
    '''
    a_line
    It can be
    "    - schema: k_syh_t_m"
    "    - {schema: k_syh_t_m}"
    return 
    "    - schema: {}"
    "    - {{schema: {}}}"
    '''       
    # get the schema name (to be replaced with {})
    schema_name = extract_schema_name(a_line)
    
    # if the original line contains {}, make them into {{}}
    result = a_line.replace("{","{{")
    result = result.replace("}","}}")
    
    result = result.replace(schema_name,"{}")

    return result
###########################################
def search_line(all_lines_lst, key_str):
    '''
    all_lines_lst: list, store all lines read from a file
    key_str: a string to be a search key
    
    return: an index (int) of all_lines_lst, all_lines_lst[indx] contains 
            exact match of key_str
    '''
    try:
        indx = all_lines_lst.index(key_str)
    except ValueError:
        # not in the list
        indx = -1
    return indx
###########################################
# the target file name
target_file_name = "default.custom.yaml"

### judge path separator: '/' (unix style) or '\' (Windows/DOS style)
path_sp = sep

#current_path = getcwd()   
# getcwd() only gives the home dir when running after pyinstaller in macOS

# argv[0] after pyinstaller, macOS app
# the actual executable file is burried in three layer deeper
# add_schema.app/Contents/MacOS/add_schema
current_path = argv[0]     # give the 0th element in the command line; the app path
current_path = abspath(current_path)   # ./ will get expanded to absolute path
current_path_splt_lst = current_path.split(path_sp)   # split to a list w/ each node
# modify current_path according the platform

## judge which platform (OS) 
# linux: linux
# macOS: darwin
# windows: win32
mySysName = platform.lower()

if mySysName.find("darwin") != -1:
    # macOS
    # commands to manipulate files
    MV='mv'
#    RM='rm'
#    CP='cp'
#    cd="cd"
    # adjust current_path (skip the last (app itself) and move three layers up)
    current_path = path_sp.join( current_path_splt_lst[:-4] )
    
elif mySysName.find("win") != -1:
    # on Windows MS-DOS
    MV='move'
#    RM='del'
#    CP='copy'
#    cd=""
    # adjust current path (skip the last (exe itself)) )
    current_path = path_sp.join( current_path_splt_lst[:-1] )

elif mySysName.find("linux") != -1:
    # linux
    # commands to manipulate files
    MV='mv'
#    RM='rm'
#    CP='cp'
#    cd="cd"
    current_path = path_sp.join( current_path_splt_lst[:-1] )
else:
    # unknown os
    raise NameError("Unknown OS. I cannot run any longer. Bye.")
    
#if in_development:
#    MV="echo mv"
#    RM="echo rm"
#    CP="echo cp"
#    cd="echo cd"
#    
#    from os import getcwd
#    current_path = getcwd()
    
    

    
# survey how many schema files are around us (in the current path)
schema_file_lst = glob(current_path + path_sp + "k_*.schema.yaml")


# True or False    
has_default_custom_file = exists(current_path + path_sp + target_file_name)

theTimeStamp = datetime.now()

if not has_default_custom_file:
    # the file does not exist
    # create a fresh one
    
    f_out_id = open(current_path + path_sp + target_file_name, "w", encoding="utf-8")
    
    print("# created by nienpo chen", file=f_out_id) 
    print("# using python script", file=f_out_id)
    print("# created: " + theTimeStamp.strftime("%Y/%m/%d, %H:%M:%S") , file=f_out_id)
    print(          file=f_out_id)
    print("patch:", file=f_out_id)  
    print("  schema_list:", file=f_out_id)
    print("    - schema: luna_pinyin     # (預設) 朙月拼音", file=f_out_id)
    
    for a_schema_path in schema_file_lst:
        
        # splitting with path_sp yields ['','Users', ...., 'rime_setting_mofifier',
        # 'k_syh_t_m.schema.yaml']
        # take the last element (index is -1)
        # "k_syh_t_m.schema.yaml"
        schema_filename = a_schema_path.split(path_sp)[-1]

        # "k_syh_t_m"
        schema_name = schema_filename.split(".")[0]
        print(" "*4 + "- schema: " + schema_name, file=f_out_id)
        
    f_out_id.close()

else:
    # pre-existing default.custom.yaml
    # read default.custom.yaml
    f_in_id = open(current_path + path_sp + target_file_name, "r", encoding="utf-8" )
    all_lines_lst = f_in_id.readlines()
    f_in_id.close()
    
    # clean up the tailing \n
    for i in range(len(all_lines_lst)):
        all_lines_lst[i] = all_lines_lst[i].rstrip()
        
    existing_schema_lst, indx_block_end = get_schema_lst(all_lines_lst)
    
    # prepare a list to store the result
    new_schema_lst = []
    
    # check if the schema file list contains new schema (not in existing_schema_lst)
    for a_schema_path in schema_file_lst:  
        # splitting with path_sp yields ['','Users', ...., 'rime_setting_mofifier',
        # 'k_syh_t_m.schema.yaml']
        # take the last element (index is -1)
        # "k_syh_t_m.schema.yaml"
        schema_filename = a_schema_path.split(path_sp)[-1]

        # "k_syh_t_m"
        schema_name = schema_filename.split(".")[0]
        
        if schema_name not in existing_schema_lst:
            # a new one
            new_schema_lst.append(schema_name)
    
    # new_schema_lst has all the new schemas to be inserted into the existing
    # default.custom.yaml
    
    if len(new_schema_lst) > 0:
        # there is at least one new schema to be added to the file
        if len(existing_schema_lst) > 0:
            # the existing default.custom.yaml file contains schema list block
            # get the existing entry to make a template
            template_str = all_lines_lst[ indx_block_end -1]
            # It can be
            # "    - schema: k_syh_t_m"
            # "    - {schema: k_syh_t_m}"
            template_str = make_template_str( template_str )
        
        else:
            # empty existing_schema_lst
            # the existing default.custom.yaml file contains NO schema list block
            line_indx = search_line(all_lines_lst, "patch:")
            if line_indx == -1:
                # no patch: header
                # add one by ourselves
                all_lines_lst.append("patch:")
            # create the block by ourselves
            # add one line at the end
            all_lines_lst.append("  schema_list:")
            
            # the value of indx_block_end was 1 when returned from get_schema_lst
            # update it to point to the next of the last line
            indx_block_end = len(all_lines_lst)
            template_str =       "    - schema: {}"
            
        
        
        for i in range(len(new_schema_lst)):
            all_lines_lst.insert(indx_block_end + i, \
                                 template_str.format( new_schema_lst[i]) )
        
        f_out_id = open(current_path + path_sp + target_file_name + ".new", "w", \
                        encoding="utf-8")
        for a_line in all_lines_lst:
            a_line = a_line.rstrip()  # removing the tailing \n, if any
            print(a_line, file=f_out_id)
        f_out_id.close()
        
        # shell/DOS command MV
        # rename (move) the original default.custom.yaml to 
        # default.custom.yaml.2020_02_15_00_33_15
        command_str=MV
        command_str=command_str + ' "' + current_path + path_sp + target_file_name + '"'
        command_str=command_str + ' "' + current_path + path_sp \
                    + target_file_name + '.' \
                    + theTimeStamp.strftime("%Y_%m_%d_%H_%M_%S") +'"'
        if system(command_str) != 0:
            raise NameError("The rename of default.custom.yaml fails.")
            
        # rename default.custom.yaml.new to default.custom.yaml
        command_str=MV
        command_str=command_str + ' "' + current_path + path_sp + target_file_name \
                    + '.new"'
        command_str=command_str + ' "' + current_path + path_sp \
                    + target_file_name +'"'
        if system(command_str) != 0:
            raise NameError("The rename of default.custom.yaml.new fails.")
    
    

    

    
          
