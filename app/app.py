# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

import os,sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0,'/Users/dtn1/gsas2full/GSASII/') # needed to "find" GSAS-II modules
import GSASIIscriptable as G2sc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# point towards directory and upload data using GSASII
ScriptDirectory=os.getcwd()
GitLabDirectory=os.path.dirname(os.getcwd())
ExampleDataDirectory=os.path.join(GitLabDirectory,"ExampleData")
SaveDataDirectory=os.path.join(GitLabDirectory,"SaveData")

datadir = os.path.expanduser(ExampleDataDirectory)
SaveDir= os.path.expanduser(SaveDataDirectory)
DataPathWrap = lambda fil: os.path.join(datadir,fil)
SaveWrap = lambda fil: os.path.join(SaveDir,fil)
gpx = G2sc.G2Project(newgpx=SaveWrap('pkfit.gpx'))
hist = gpx.add_powder_histogram(DataPathWrap('Gonio_BB-HD-Cu_Gallipix3d[30-120]_New_Control_proper power.xrdml'),
                                DataPathWrap('TestCalibration.instprm'), # need to get a 
                                fmthint='Panalytical xrdml (xml)', databank=1, instbank=1)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#df = pd.DataFrame({
#    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#    "Amount": [4, 1, 2, 2, 4, 5],
#    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
#})

#fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

df = pd.DataFrame({
        "two_theta":hist.data['data'][1][0],
        "intensity":hist.data['data'][1][1]
})

fig = px.line(df,x='two_theta',y='intensity',title='Peak Fitting Plot')

app.layout = html.Div(children=[
    html.H2(children='Austenite Calculator'),

    html.Div(children='''
        Austenite Calculator: A calculator for austenite.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server()
