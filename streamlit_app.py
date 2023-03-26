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
with st.sidebar:
    language = st.selectbox('Wybierz język aplikacji/Select app language', ['Polish', 'English'])

def load_files(path):
    dir_path = f'{path}/patient*'
    res = glob.glob(dir_path)
    # return [file for file in os.listdir(path) if 'patient' in file]
    return res

def load_record_file(record_name):
    return wfdb.rdsamp(record_name=record_name[:-4])

if 'done_diagnosis' not in st.session_state:
    st.session_state['diagnosed'] = False

if 'patient_diagnosis' not in st.session_state:
    st.session_state['patient_diagnosis'] = None

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
        patient_files_label = [l.replace("Patient", "Pacjent") for l in patient_files_label]
        patients_selection = [st.selectbox('Wybierz pacjenta', patient_files_label).replace("Pacjent", "Patient")]
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
    if col2.button('Filtruj Sygnał' if language=='Polish' else 'Filter Signals'):
        for participant in patients_selection:
            dir = path+'patient'+participant.split('Patient ')[-1]
            filename = glob.glob(dir+'/*.dat*')[0]
            file = filename
            data = pd.DataFrame()
            rec = load_record_file(file)
            signal = rec[0][:, 0]
            rand_value = random.randint(5000, signal.shape[0]-5000)
            rand_range = (rand_value, rand_value+5000)
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
                diagnosis_options = {
                "Cardiomyopathy": "Kardiomiopatia",
                "Healthy control": "Zdrowy pacjent",
                "Bundle branch block": "Blokada odnogi pęczka Hisa",
                "Myocarditis": "Zapalenie mięśnia sercowego",
                "Myocardial infarction": "Zawał serca",
                }
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Pacjent '+re.split('Patient', participant)[-1]+' - '+diagnosis_options[Admission.split('Reason for admission: ')[1]])
            else:
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Patient '+re.split('Patient', participant)[-1]+' - '+Admission.split('Reason for admission: ')[1])
            fig2.update_layout(autosize=True,
                  height=800)
            col10.plotly_chart(fig, use_container_width=False)   
            col11.plotly_chart(fig2, use_container_width=False)
else:
    if language=='Polish':
        patient_files_label = ['Pacjent '+file.split('/patient')[-1] for file in patient_files]
        patients_selection = [st.selectbox('Wybierz pacjenta', patient_files_label).replace("Pacjent", "Patient")]
    else:
        patient_files_label = ['Patient '+file.split('/patient')[-1] for file in patient_files]
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
    diagnosis_anaylysed = ['Cardiomyopathy','Healthy control','Bundle branch block','Myocarditis','Myocardial infarction']
    if st.session_state.patient_diagnosis in diagnosis_anaylysed:
        with st.form(key='my_form'):
            if language=='Polish':
                diagnosis_options = {
                0: "Kardiomiopatia",
                1: "Zdrowy pacjent",
                2: "Blokada odnogi pęczka Hisa",
                3: "Zapalenie mięśnia sercowego",
                4: "Zawał serca",
                }
                diagnosis_selected = st.radio("Spróbuj zdiagnozować pacjenta", options = (0, 1, 2, 3, 4), format_func=lambda x: diagnosis_options.get(x))
                diagnosis = diagnosis_anaylysed[diagnosis_selected]
            else:
                diagnosis_options = {
                0: "Cardiomyopathy",
                1: "Healthy control",
                2: "Bundle branch block",
                3: "Myocarditis",
                4: "Myocardial infarction",
                }
                diagnosis_selected = st.radio("Try to diagnose patient", options = (0, 1, 2, 3, 4), format_func=lambda x: diagnosis_options.get(x)) 
                diagnosis = diagnosis_anaylysed[diagnosis_selected]
            submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                st.session_state.diagnosed = True
                if diagnosis == st.session_state.patient_diagnosis:
                    if language=='Polish':
                        st.write('Poprawna diagnoza! 🔥')
                    else:
                        st.write('Correct diagnosis! 🔥')
                else:
                    if language=='Polish':
                        st.write('Niepoprawna diagnoza! 😔')
                    else:
                        st.write('Incorrect diagnosis! 😔')
    else:
        if language=='Polish':
            st.write('Choroba tego pacjenta jest poza zakresem laboratorium')
        else:
            st.write('Diagnosis of this patient is out of laboratory scope')

    if st.session_state.diagnosed or col2.button('Filtruj Sygnał' if language=='Polish' else 'Filter Signals'):
        for participant in patients_selection:
            dir = path+'patient'+participant.split('Patient ')[-1]
            filename = glob.glob(dir+'/*.dat*')[0]
            file = filename
            data = pd.DataFrame()
            rec = load_record_file(file)
            signal = rec[0][:, 0]
            rand_value = random.randint(5000, signal.shape[0]-5000)
            rand_range = (rand_value, rand_value+5000)
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
            st.session_state.patient_diagnosis = Admission.split('Reason for admission: ')[1]
            data["Sex"] = rec[1]['comments'][1]
            data["Age"] = rec[1]['comments'][0]
            if language=='Polish':
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Pacjent '+re.split('Patient', participant)[-1])
            else:
                fig.update_layout(autosize=True,
                  height=800,
                  title_text='Patient '+re.split('Patient', participant)[-1])
            # st.write(Admission)
            fig2.update_layout(autosize=True,
                  height=800)
            col10.plotly_chart(fig, use_container_width=False)   
            col11.plotly_chart(fig2, use_container_width=False)