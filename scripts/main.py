# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:28:25 2026

@author: cetae
"""

# main.py
import subprocess

print("Running Data Ingestion...")
subprocess.run(["python", "bdj_gbif_mhhp_input_2026_2.py"])

print("Running Ecological Modeling...")
subprocess.run(["python", "bdj_gbif_mhhp_model_2026.py"])