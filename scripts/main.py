# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:28:25 2026

@author: cetae
"""

# main.py
import subprocess

print("Running Data Extraction...")
subprocess.run(["python", "1_bdj_gbif_mhhp_input_2026.py"])

print("Running Species Accumulation Curve (SAC)...")
subprocess.run(["python", "2_bdj_gbif_mhhp_SAC_2026.py"])



