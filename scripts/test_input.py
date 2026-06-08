# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 17:19:59 2026

@author: cetae
"""
import os
from pathlib import Path
import matplotlib

print(f'The backend of graphic is {matplotlib.get_backend()}')

# Returns the absolute directory of the active script
script_dir = Path(__file__).resolve().parent
print(script_dir)


print(f'script_dir is {script_dir}')
print(f'realpath is {os.path.realpath(__file__)}')
print(f'abspath is {os.path.abspath(__file__)}')





try:
    script_dir = os.path.abspath(__file__)
except:
    script_dir = os.getcwd()
    
    
root_path = os.path.abspath(os.path.join(script_dir, '..'))

print(f'root_path  is {root_path }')
