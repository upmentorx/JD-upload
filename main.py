import streamlit as st
import requests
import time

st.set_page_config(page_title="PDF Uploader to n8n", page_icon="📄", layout="centered")

st.title("📄 PDF Upload to n8n & Drive")
st.markdown("""
**Please follow these instructions:**
- Upload **only one PDF file at a time**.
- File size should be reasonable for upload.
- After uploading, please wait **1 minute** before uploading the next PDF.
""")

if "last_upload_time" not in st.session_state:
    st.session_state["last_upload_time"] = 0

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

def can_upload():
    # Check if 1 minute has passed since last upload
    return time.time() - st.session_state["last_upload_time"] >= 60

if uploaded_file is not None:
    if not can_upload():
        remaining = int(60 - (time.time() - st.session_state["last_upload_time"]))
        st.warning(f"Please wait {remaining} seconds before uploading another PDF.")
    else:
        # Show filename and size for user confirmation
        st.write(f"**Selected File:** {uploaded_file.name}  ({uploaded_file.size / 1024:.2f} KB)")

        if st.button("Upload PDF"):
            with st.spinner("Uploading your PDF..."):
                file_bytes = uploaded_file.getvalue()
                webhook_url = "https://hirednext.app.n8n.cloud/webhook-test/48ee35d3-75ef-430c-a734-d5971d3c5edc"  # Change this to your n8n webhook URL

                files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                try:
                    response = requests.post(webhook_url, files=files)
                    if response.ok:
                        st.success("🎉 PDF successfully sent to n8n!")
                        st.session_state["last_upload_time"] = time.time()  # Reset timer
                    else:
                        st.error(f"Upload failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Show countdown timer if waiting
if not can_upload():
    remaining = int(60 - (time.time() - st.session_state["last_upload_time"]))
    st.info(f"Next upload available in {remaining} seconds.")

