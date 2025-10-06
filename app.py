import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile

st.set_page_config(page_title="JD PDF Uploader", layout="centered")
st.title("Job Description PDF Uploader")
st.markdown("Upload your **PDF files only** to automatically save them to the JD folder in Google Drive.")

@st.cache_resource  # Cache authentication for the session
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = 'client_secrets.json'
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

drive = authenticate_drive()

uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded:
    with st.spinner(f"Uploading {uploaded.name} to Google Drive (JD folder)..."):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(uploaded.read())
        temp_file.close()

        folder_id = "12Hwf5I4aQ8kLFUa04zCp1ziLG9TJPCF7"
        file_drive = drive.CreateFile({'title': uploaded.name, 'parents': [{'id': folder_id}]})
        file_drive.SetContentFile(temp_file.name)
        file_drive.Upload()

        st.success(f"✅ {uploaded.name} has been uploaded successfully to the JD folder in Google Drive!")

st.markdown("---")
st.info("Please only upload PDF files.")
