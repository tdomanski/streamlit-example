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
st.set_page_config(
    page_title="Electrophysiology Labs",
    page_icon="🧊",
    layout="wide"
)

language = st.selectbox('Select a language', ['Polish', 'English'])

def load_files(path):
    dir_path = f'{path}/patient*'
    res = glob.glob(dir_path)
    # return [file for file in os.listdir(path) if 'patient' in file]
    return res

def load_record_file(record_name):
    return wfdb.rdsamp(record_name=record_name[:-4])

if 'done_diagnosis' not in st.session_state:
    st.session_state['diagnosed'] = False

if language=='Polish':
    st.title('Analiza sygnału EKG')
else:
    st.title('ECG Signal Analysis')

path = 'physionet.org/files/ptbdb/1.0.0/'
patient_files = load_files(path)
if language=='Polish':
    demo_mode = st.checkbox('Tryb demo 😎', value=True)
else:
    demo_mode = st.checkbox('Demo Mode 😎', value=True)
if demo_mode:
    patient_files_label = ['Patient 001', 'Patient 002']
    if language=='Polish':
        patients_selection = [st.selectbox('Wybierz pacjenta', patient_files_label)]
    else:
        patients_selection = [st.selectbox('Choose patient', patient_files_label)]
    code = '''import neurokit2 as nk'''
    st.code(code, language='python')
    if language=='Polish':
        link='[Dokumentacja NeuroKit2](https://neuropsychology.github.io/NeuroKit/index.html)'
    else:
        link='[NeuroKit2 Documentation](https://neuropsychology.github.io/NeuroKit/index.html)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col7, col8 = st.columns(2)
    with col1:
        if language=='Polish':
            lowcut = st.number_input('Podaj dolny próg filtracji', value=0.05)
        else:
            lowcut = st.number_input('Insert a lowcut number', value=0.05)
    with col2:
        if language=='Polish':
            highcut = st.number_input('Podaj górny próg filtracji', value=150)
        else:
            highcut = st.number_input('Insert a highcut number', value=150)
    with col3:
        if language=='Polish':
            method = st.selectbox('Wybierz metodę filtracji', ['butterworth', 'fir', 'bessel', 'savgol'])
        else:
            method = st.selectbox('Select a method for signal filtration', ['butterworth', 'fir', 'bessel', 'savgol'])
    if method == 'butterworth' or method == 'savgol':
        with col4:
            if language=='Polish':
                order = st.number_input('Podaj numer rzędu (Butterworth & Savgol)', value=2)
            else:
                order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2)
    else:
        with col4:
            if language=='Polish':
                order = st.number_input('Podaj numer rzędu (Butterworth & Savgol)', value=2, disabled=True)
            else:
                order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2, disabled=True)
    with col7:
        if language=='Polish':
            powerline = st.number_input('Podaj numer linii mocy', value=50)
        else:
            powerline = st.number_input('Insert a powerline number', value=50)
    if language=='Polish':
        code='''przefiltrowany_sygnal = nk.signal_filter(sygnal, dolny_prog, gorny_prog, metoda, rzad, moc_linii)'''
    else:
        code = '''filtered_signal = nk.signal_filter(input_signal, lowcut, highcut, method, order, powerline)'''
    st.code(code, language='python')
    if language=='Polish':
        link='Funkcja: [nk.signal_filter](https://neuropsychology.github.io/NeuroKit/functions/signal.html#signal-filter)'
    else:
        link='Function: [nk.signal_filter](https://neuropsychology.github.io/NeuroKit/functions/signal.html#signal-filter)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    if col2.button('Filter Signals'):
        for participant in patients_selection:
            dir = path+'patient'+participant.split('Patient ')[-1]
            filename = glob.glob(dir+'/*.dat*')[0]
            file = filename
            data = pd.DataFrame()
            rec = load_record_file(file)
            signal = rec[0][:, 0]
            rand_value = random.randint(1000, signal.shape[0]-1000)
            rand_range = (rand_value, rand_value+3000)
            fig = make_subplots(rows=12, cols=1, shared_xaxes=True)
            fig2 = make_subplots(rows=12, cols=1, shared_xaxes=True)
            col10, col11 = st.columns(2)
            for i in range(12):
                signal_name = rec[1]['sig_name'][i]
                signal = rec[0][:, i]
                channel = pd.DataFrame({str(signal_name): rec[0][:, 0]})
                data = pd.concat([data, channel], axis=1)
                signal = nk.signal_filter(signal, lowcut=lowcut,highcut = highcut,method='butterworth', order=2, window_size='default', powerline=50, show=False)
                signal_good = nk.signal_filter(signal, lowcut=0.05,highcut = 150,method='butterworth', order=2, window_size='default', powerline=50, show=False)
                fig.append_trace(go.Scatter(y=signal[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name=signal_name),row=i+1, col=1)
                fig2.append_trace(go.Scatter(y=signal_good[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name=signal_name),row=i+1, col=1)                
            data["Participant"] = re.split('Patient', participant)[-1]
            data["Sample"] = range(len(data))
            data["Sampling_Rate"] = 1000
            Admission = rec[1]['comments'][4]
            data["Sex"] = rec[1]['comments'][1]
            data["Age"] = rec[1]['comments'][0]
            if language=='Polish':
                st.write('Pacjent '+re.split('Patient', participant)[-1])
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Pacjent '+re.split('Pacjent', participant)[-1]+' - '+Admission)
            else:
                st.write('Patient '+re.split('Patient', participant)[-1])
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Pacjent '+re.split('Patient', participant)[-1]+' - '+Admission)
            # st.write(Admission)
            fig2.update_layout(autosize=True,
                  height=800)
            col10.plotly_chart(fig, use_container_width=False)   
            col11.plotly_chart(fig2, use_container_width=False)
else:
    patient_files_label = ['Patient '+file.split('/patient')[-1] for file in patient_files]
    if language=='Polish':
        patients_selection = [st.selectbox('Wybierz pacjenta', patient_files_label)]
    else:
        patients_selection = [st.selectbox('Choose patient', patient_files_label)]
    code = '''import neurokit2 as nk'''
    st.code(code, language='python')
    if language=='Polish':
        link='[Dokumentacja NeuroKit2](https://neuropsychology.github.io/NeuroKit/index.html)'
    else:
        link='[NeuroKit2 Documentation](https://neuropsychology.github.io/NeuroKit/index.html)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col7, col8 = st.columns(2)
    with col1:
        if language=='Polish':
            lowcut = st.number_input('Podaj dolny próg filtracji', value=0.05)
        else:
            lowcut = st.number_input('Insert a lowcut number', value=0.05)
    with col2:
        if language=='Polish':
            highcut = st.number_input('Podaj górny próg filtracji', value=150)
        else:
            highcut = st.number_input('Insert a highcut number', value=150)
    with col3:
        if language=='Polish':
            method = st.selectbox('Wybierz metodę filtracji', ['butterworth', 'fir', 'bessel', 'savgol'])
        else:
            method = st.selectbox('Select a method for signal filtration', ['butterworth', 'fir', 'bessel', 'savgol'])
    if method == 'butterworth' or method == 'savgol':
        with col4:
            if language=='Polish':
                order = st.number_input('Podaj numer rzędu (Butterworth & Savgol)', value=2)
            else:
                order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2)
    else:
        with col4:
            if language=='Polish':
                order = st.number_input('Podaj numer rzędu (Butterworth & Savgol)', value=2, disabled=True)
            else:
                order = st.number_input('Insert an order number (Butterworth & Savgol)', value=2, disabled=True)
    with col7:
        if language=='Polish':
            powerline = st.number_input('Podaj numer linii mocy', value=50)
        else:
            powerline = st.number_input('Insert a powerline number', value=50)
    if language=='Polish':
        code='''przefiltrowany_sygnal = nk.signal_filter(sygnal, dolny_prog, gorny_prog, metoda, rzad, moc_linii)'''
    else:
        code = '''filtered_signal = nk.signal_filter(input_signal, lowcut, highcut, method, order, powerline)'''
    st.code(code, language='python')
    if language=='Polish':
        link='Funkcja: [nk.signal_filter](https://neuropsychology.github.io/NeuroKit/functions/signal.html#signal-filter)'
    else:
        link='Function: [nk.signal_filter](https://neuropsychology.github.io/NeuroKit/functions/signal.html#signal-filter)'
    st.markdown(link,unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    diagnosis_anaylysed = ('Cardiomyopathy','Healthy control','Bundle branch block','Myocarditis','Myocardial infarction')
    if st.session_state.diagnosed or col2.button('Filter Signals'):
        for participant in patients_selection:
            dir = path+'patient'+participant.split('Patient ')[-1]
            filename = glob.glob(dir+'/*.dat*')[0]
            file = filename
            data = pd.DataFrame()
            rec = load_record_file(file)
            signal = rec[0][:, 0]
            rand_value = random.randint(1000, signal.shape[0]-1000)
            rand_range = (rand_value, rand_value+3000)
            fig = make_subplots(rows=12, cols=1, shared_xaxes=True)
            fig2 = make_subplots(rows=12, cols=1, shared_xaxes=True)
            col10, col11 = st.columns(2)
            for i in range(12):
                signal_name = rec[1]['sig_name'][i]
                signal = rec[0][:, i]
                channel = pd.DataFrame({str(signal_name): rec[0][:, 0]})
                data = pd.concat([data, channel], axis=1)
                signal = nk.signal_filter(signal, lowcut=lowcut,highcut = highcut,method='butterworth', order=2, window_size='default', powerline=50, show=False)
                signal_good = nk.signal_filter(signal, lowcut=0.05,highcut = 150,method='butterworth', order=2, window_size='default', powerline=50, show=False)
                fig.append_trace(go.Scatter(y=signal[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name=signal_name),row=i+1, col=1)
                fig2.append_trace(go.Scatter(y=signal_good[rand_range[0]:rand_range[1]],
                                mode='lines',
                                name=signal_name),row=i+1, col=1)                
            data["Participant"] = re.split('Patient', participant)[-1]
            data["Sample"] = range(len(data))
            data["Sampling_Rate"] = 1000
            Admission = rec[1]['comments'][4]
            data["Sex"] = rec[1]['comments'][1]
            data["Age"] = rec[1]['comments'][0]
            if language=='Polish':
                st.write('Pacjent '+re.split('Patient', participant)[-1])
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Pacjent '+re.split('Pacjent', participant)[-1]+' - '+Admission)
            else:
                st.write('Patient '+re.split('Patient', participant)[-1])
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Pacjent '+re.split('Patient', participant)[-1]+' - '+Admission)
            # st.write(Admission)
            fig2.update_layout(autosize=True,
                  height=800)
            col10.plotly_chart(fig, use_container_width=False)   
            col11.plotly_chart(fig2, use_container_width=False)
        if Admission.split('Reason for admission: ')[1] in diagnosis_anaylysed:
            with st.form(key='my_form'):
                diagnosis = st.radio("Try to diagnose patient", ('Cardiomyopathy','Dysrhythmia','Hypertrophy','Valvular heart disease','Dysrhythmia','Healthy control','Bundle branch block','Myocarditis','Myocardial infarction','Unstable angina','Stable angina','Heart failure (NYHA 2)','Heart failure (NYHA 3)','Palpitation','Heart failure (NYHA 4)')) 
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    st.session_state.diagnosed = True
                    if diagnosis == Admission.split('Reason for admission: ')[1]:
                        st.write('Correct diagnosis! 🔥')
                    else:
                        st.write('Incorrect diagnosis! 😔')
        else:
            st.write('Patient diagnosis not covered in this labs')