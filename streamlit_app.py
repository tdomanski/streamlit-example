from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import neurokit2 as nk
import wfdb
import os
import numpy as np

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""
def load_files(path):
    return [file for file in os.listdir(path) if 'patient' in file]

with st.echo(code_location='below'):
    wd = os.getcwd()
    path = ''
    patient_files = load_files(path)
    for participant in patient_files:
        path = wd + path + participant
        filename = [i for i in os.listdir(path) if ".dat" in i][0]
        file = path + "/" + filename
        for i in range(12):
            signal_name = wfdb.rdsamp(record_name=file[:-4])[1]['sig_name'][i]
            signal = wfdb.rdsamp(record_name=file[:-4])[0][:, i]
            channel = pd.DataFrame({str(signal_name): wfdb.rdsamp(record_name=file[:-4])[0][:, 0]})
            data = pd.concat([data, channel], axis=1)

            #filter lowpasshighpass and powerline
            signal_ok = nk.signal_filter(signal, lowcut=0.05,highcut = 150,method='butterworth', order=2, window_size='default', powerline=50, show=False)
            
            signal_notok = nk.signal_filter(signal, lowcut=0.5,highcut = 40,method='butterworth', order=2, window_size='default', powerline=50, show=False)
        data["Participant"] = participant
        data["Sample"] = range(len(data))
        data["Sampling_Rate"] = 1000
        data["Database"] = "PTB-Diagnostic-ECG-Database-1.0.0"
        data["Sex"] = wfdb.rdsamp(file[:-4])[1]['comments'][1]
        data["Age"] = wfdb.rdsamp(file[:-4])[1]['comments'][0]
    # total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
    # num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

    # Point = namedtuple('Point', 'x y')
    # data = []

    # points_per_turn = total_points / num_turns

    # for curr_point_num in range(total_points):
    #     curr_turn, i = divmod(curr_point_num, points_per_turn)
    #     angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
    #     radius = curr_point_num / total_points
    #     x = radius * math.cos(angle)
    #     y = radius * math.sin(angle)
    #     data.append(Point(x, y))

    # st.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
    #     .mark_circle(color='#0068c9', opacity=0.5)
    #     .encode(x='x:Q', y='y:Q'))
