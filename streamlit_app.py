import pandas as pd
import streamlit as st
import neurokit2 as nk
import wfdb
import glob
import re
import plotly.graph_objects as go
import random
from plotly.subplots import make_subplots

# """
# # Welcome to Streamlit!

# Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

# If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
# forums](https://discuss.streamlit.io).

# In the meantime, below is an example of what you can do with just a few lines of code:
# """
def load_files(path):
    dir_path = f'{path}/patient*'
    res = glob.glob(dir_path)
    # return [file for file in os.listdir(path) if 'patient' in file]
    return res

def load_record_file(record_name):
    return wfdb.rdsamp(record_name=record_name[:-4])

if 'done_diagnosis' not in st.session_state:
    st.session_state['diagnosed'] = False

st.title('ECG Signal Analysis')
# with st.echo():
path = 'physionet.org/files/ptbdb/1.0.0/'
patient_files = load_files(path)
if st.checkbox('Demo Mode 😎', value=True):
    patient_files_label = ['Patient 001', 'Patient 002']
    patients_selection = [st.selectbox('Choose patient', patient_files_label)]
    code = '''import neurokit2 as nk'''
    st.code(code, language='python')
    link='[NeuroKit2 Documentation](https://neuropsychology.github.io/NeuroKit/index.html)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col7, col8 = st.columns(2)
    with col1:
        lowcut = st.number_input('Insert a lowcut number', value=0.05)
    with col2:
        highcut = st.number_input('Insert a highcut number', value=150)
    with col3:
        method = st.selectbox('Select a method for signal filtration', ['butterworth', 'fir', 'bessel', 'savgol'])
    if method == 'butterworth' or method == 'savgol':
        with col4:
            order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2)
    else:
        with col4:
            order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2, disabled=True)
    with col7:
        powerline = st.number_input('Insert a powerline number', value=50)
    code = '''filtered_signal = nk.signal_filter(input_signal, lowcut, highcut, method, order, powerline)'''
    st.code(code, language='python')
    link='Function: [nk.signal_filter](https://neuropsychology.github.io/NeuroKit/functions/signal.html#signal-filter)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    if col2.button('Filter Signals'):
        for participant in patients_selection:
            dir = path+'patient'+participant.split('Patient ')[-1]
            filename = glob.glob(dir+'/*.dat*')[0]
            file = filename
            data = pd.DataFrame()
            for i in range(12):
                rec = load_record_file(file)
                signal_name = rec[1]['sig_name'][i]
                signal = rec[0][:, i]
                channel = pd.DataFrame({str(signal_name): rec[0][:, 0]})
                data = pd.concat([data, channel], axis=1)

                #filter lowpasshighpass and powerline
                signal = nk.signal_filter(signal, lowcut=lowcut,highcut = highcut,method='butterworth', order=2, window_size='default', powerline=50, show=False)
                signal_good = nk.signal_filter(signal, lowcut=0.05,highcut = 150,method='butterworth', order=2, window_size='default', powerline=50, show=False)
            data["Participant"] = re.split('Patient', participant)[-1]
            data["Sample"] = range(len(data))
            data["Sampling_Rate"] = 1000
            # data["Database"] = "PTB-Diagnostic-ECG-Database-1.0.0"
            Admission = rec[1]['comments'][4]
            data["Sex"] = rec[1]['comments'][1]
            data["Age"] = rec[1]['comments'][0]
            st.write('Patient '+re.split('Patient', participant)[-1])
            st.write(Admission)
            fig = go.Figure()
            rand_value = random.randint(1000, signal.shape[0]-1000)
            rand_range = (rand_value, rand_value+1000)
            fig.add_trace(go.Scatter(y=signal[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name='Custom Filter Settings'))
            fig.add_trace(go.Scatter(y=signal_good[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name='Good Filter Settings'))
            fig.update_xaxes(minor=dict(ticklen=6, tickcolor="gray", tickmode='auto', nticks=5, showgrid=True))
            fig.update_yaxes(minor_ticks="inside")
            st.plotly_chart(fig)   
else:
    patient_files_label = ['Patient '+file.split('/patient')[-1] for file in patient_files]
    patients_selection = [st.selectbox('Choose patient', patient_files_label)]
    code = '''import neurokit2 as nk'''
    st.code(code, language='python')
    link='[NeuroKit2 Documentation](https://neuropsychology.github.io/NeuroKit/index.html)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col7, col8 = st.columns(2)
    with col1:
        lowcut = st.number_input('Insert a lowcut number', value=0.05)
    with col2:
        highcut = st.number_input('Insert a highcut number', value=150)
    with col3:
        method = st.selectbox('Select a method for signal filtration', ['butterworth', 'fir', 'bessel', 'savgol'])
    if method == 'butterworth' or method == 'savgol':
        with col4:
            order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2)
    else:
        with col4:
            order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2, disabled=True)
    with col7:
        powerline = st.number_input('Insert a powerline number', value=50)
    code = '''filtered_signal = nk.signal_filter(input_signal, lowcut, highcut, method, order, powerline)'''
    st.code(code, language='python')
    link='Function: [nk.signal_filter](https://neuropsychology.github.io/NeuroKit/functions/signal.html#signal-filter)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with st.form(key='my_form'):
        diagnosis = st.radio("Try to diagnose patient", ('Cardiomyopathy','Dysrhythmia','Hypertrophy','Valvular heart disease','Dysrhythmia','Healthy control','Bundle branch block','Myocarditis','Myocardial infarction','Unstable angina','Stable angina','Heart failure (NYHA 2)','Heart failure (NYHA 3)','Palpitation','Heart failure (NYHA 4)')) 
        submit_button = st.form_submit_button(label='Submit')
        if submit_button:
            st.session_state.diagnosed = True
            if diagnosis == 'Cardiomyopathy':
                st.write('Correct diagnosis! 🔥')
            else:
                st.write('Incorrect diagnosis! 😔')
    if st.session_state.diagnosed or col2.button('Filter Signals'):
        for participant in patients_selection:
            dir = path+'patient'+participant.split('Patient ')[-1]
            filename = glob.glob(dir+'/*.dat*')[0]
            file = filename
            data = pd.DataFrame()
            rec = load_record_file(file)
            signal = rec[0][:, 0]
            rand_value = random.randint(1000, signal.shape[0]-1000)
            rand_range = (rand_value, rand_value+1000)
            # fig = go.Figure()
            fig = make_subplots(rows=12, cols=1)
            for i in range(12):
                signal_name = rec[1]['sig_name'][i]
                signal = rec[0][:, i]
                channel = pd.DataFrame({str(signal_name): rec[0][:, 0]})
                data = pd.concat([data, channel], axis=1)

                #filter lowpasshighpass and powerline
                signal = nk.signal_filter(signal, lowcut=lowcut,highcut = highcut,method='butterworth', order=2, window_size='default', powerline=50, show=False)
                # fig.add_trace(go.Scatter(y=signal[rand_range[0]:rand_range[1]],
                #                 mode='lines',
                #                 name=signal_name))
                fig.append_trace(go.Scatter(y=signal[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name=signal_name))
            data["Participant"] = re.split('Patient', participant)[-1]
            data["Sample"] = range(len(data))
            data["Sampling_Rate"] = 1000
            # data["Database"] = "PTB-Diagnostic-ECG-Database-1.0.0"
            Admission = rec[1]['comments'][4]
            data["Sex"] = rec[1]['comments'][1]
            data["Age"] = rec[1]['comments'][0]
            st.write('Patient '+re.split('Patient', participant)[-1])
            # st.write(Admission)

            # fig = go.Figure()
            # fig.add_trace(go.Scatter(y=signal[rand_range[0]:rand_range[1]],
            #                     mode='lines',
            #                     name='Custom Filter Settings'))
            # fig.add_trace(go.Scatter(y=signal_good[rand_range[0]:rand_range[1]],
            #                     mode='lines',
            #                     name='Good Filter Settings'))
            fig.update_xaxes(minor=dict(ticklen=6, tickcolor="gray", tickmode='auto', nticks=5, showgrid=True))
            fig.update_yaxes(minor_ticks="inside")
            st.plotly_chart(fig, use_container_width=True)
            # fig, ax = plt.subplots()
            # # ax.plot(signal_notok, color = 'r')
            # ax.plot(signal_ok, color='g')
            # ax.set_ylabel('Amplitude [mV]')
            # ax.set_xlabel('Time [ms]')
            # ax.set_title(signal_name)
            # ax.set_xlim([1400,2800])
            # ax.set_ylim([-1.5, 1.5])
            # ax.yaxis.grid(which='major', color='grey', linewidth=1.2)
            # ax.yaxis.grid(which='minor', color='grey', linewidth=0.6)
            # ax.xaxis.grid(which='major', color='grey', linewidth=1.2)
            # ax.xaxis.grid(which='minor', color='grey', linewidth=0.6)
            # st.pyplot(fig)
            # ax.yaxis.set_minor_locator(AutoMinorLocator(5))
            # ax.xaxis.set_minor_locator(AutoMinorLocator(5))