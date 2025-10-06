import json
import tempfile
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

st.set_page_config(page_title="JD PDF Uploader", layout="centered")
st.title("Job Description PDF Uploader")
st.markdown("Upload your **PDF files only** to automatically save them to the JD folder in Google Drive.")

# --------------- Build client_secrets from Streamlit secrets ----------------
# Expect st.secrets["google_oauth"] to contain keys: client_id, client_secret,
# auth_uri, token_uri and optionally redirect_uris (list)
google_oauth = st.secrets.get("google_oauth", None)
if google_oauth is None:
    st.error("Google OAuth secrets not found. Add google_oauth keys to Streamlit secrets.")
    st.stop()

client_config = {
    "installed": {
        "client_id": google_oauth["client_id"],
        "project_id": google_oauth.get("project_id", ""),
        "auth_uri": google_oauth.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": google_oauth.get("token_uri", "https://oauth2.googleapis.com/token"),
        "auth_provider_x509_cert_url": google_oauth.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
        "client_secret": google_oauth["client_secret"],
        "redirect_uris": google_oauth.get("redirect_uris", ["http://localhost:8090/"])
    }
}

# Write the client_config to a temporary file and keep its path
@st.cache_resource
def make_client_secrets_file():
    tf = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    json.dump(client_config, tf)
    tf.flush()
    return tf.name

client_secrets_path = make_client_secrets_file()

# --------------- Authenticate with PyDrive2 (cached per session) ----------------
@st.cache_resource
def authenticate_drive(secrets_path):
    gauth = GoogleAuth()
    # instruct PyDrive2 to use the generated client_secrets file
    gauth.DEFAULT_SETTINGS['client_config_file'] = secrets_path
    # run the local webserver auth (opens browser for consent)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

drive = authenticate_drive(client_secrets_path)

# --------------- File uploader and upload into JD folder ----------------
uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])
if uploaded:
    with st.spinner(f"Uploading {uploaded.name} to Google Drive (JD folder)..."):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(uploaded.read())
        tmp.flush()
        tmp.close()

        folder_id = "12Hwf5I4aQ8kLFUa04zCp1ziLG9TJPCF7"  # replace if needed
        file_drive = drive.CreateFile({'title': uploaded.name, 'parents': [{'id': folder_id}]})
        file_drive.SetContentFile(tmp.name)
        file_drive.Upload()
        st.success(f"✅ {uploaded.name} has been uploaded successfully to the JD folder in Google Drive!")

st.markdown("---")
st.info("Please only upload PDF files.")
