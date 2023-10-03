# plotting
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.utils as pltu
from plotly.tools import mpl_to_plotly

# utils
import base64
import io
import os
import platform
import re
import sys
import shutil
import fnmatch
import glob
import random
import math
from copy import deepcopy
import json

# Add example comment

# user created
sys.path.insert(0,'/root/AustCalc/app')
import compute_results
import compute_uncertainties
import interaction_vol

# Gsas
if platform.system() == 'Linux':
    sys.path.insert(0,'/root/g2full/GSASII/') 
    inside_docker = True

elif re.search('creuzige',os.getcwd()):
    sys.path.insert(0, '/Users/creuzige/gsas2full/envs/gsas-AustCalc/GSASII/')

import GSASIIscriptable as G2sc
import GSASIIpath

try:
    GSASIIpath.svnUpdateDir(version=5300,verbose=True)
except Exception: #GSAS raises an execption if unable to connect to svn
    print("Unable to update, using whichever version is installed")

# example 5

datadir, cif_fnames, workdir, xrdml_fnames, instprm_fname, json_fname = compute_results.gather_example('5')

with open(os.path.join(datadir, json_fname), 'r') as f:
    crystal_data = json.loads(f.read())

