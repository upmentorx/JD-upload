import streamlit as st
import requests
import time

st.set_page_config(page_title="PDF Uploader to n8n", page_icon="📄", layout="centered")

st.title("📄 PDF Upload to n8n & Drive")
st.markdown(
    """
**Please follow these instructions:**
- Upload **only one PDF file at a time**.
- File size should be reasonable for upload.
- After uploading, please wait **1 minute** before uploading the next PDF.
"""
)

if "last_upload_time" not in st.session_state:
    st.session_state["last_upload_time"] = 0

# Email options
EMAIL_OPTIONS = [
    "prathyusha.m@hirednext.info",
    "rinkal@hirednext.info",
    "pratyusha@hirednext.info",
]

# --- EMAIL SELECTION SECTION ---
st.subheader("Select emails to associate with this upload")

# Use checkboxes for multiple selection
selected_emails = []
cols = st.columns(len(EMAIL_OPTIONS))
for i, email in enumerate(EMAIL_OPTIONS):
    with cols[i]:
        if st.checkbox(email, key=f"email_{i}"):
            selected_emails.append(email)

# Require at least one email to be selected
if not selected_emails:
    st.warning("⚠️ Please select at least one email before uploading.")

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

        # Show selected emails
        st.markdown("**Selected emails:**")
        for email in selected_emails:
            st.write(f"- {email}")

        if st.button("Upload PDF"):
            if not selected_emails:
                st.error("Please select at least one email before uploading.")
            else:
                with st.spinner("Uploading your PDF..."):
                    try:
                        file_bytes = uploaded_file.getvalue()
                        webhook_url = "https://hirednext.app.n8n.cloud/webhook/48ee35d3-75ef-430c-a734-d5971d3c5edc"  # Replace with your n8n webhook URL

                        # Prepare files and data
                        files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                        data = {
                            "emails": ", ".join(selected_emails),
                            "filename": uploaded_file.name,
                        }

                        response = requests.post(webhook_url, files=files, data=data, timeout=60)
                        if response.ok:
                            st.success("🎉 PDF successfully sent to n8n!")
                            st.session_state["last_upload_time"] = time.time()  # Reset timer
                        else:
                            st.error(f"Upload failed: {response.status_code} — {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Show countdown timer if waiting
if not can_upload():
    remaining = int(60 - (time.time() - st.session_state["last_upload_time"]))
    st.info(f"Next upload available in {remaining} seconds.")
