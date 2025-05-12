import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import pickle
import io
import google.auth
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup


# 1. Streamlit UI – collect user inputs
st.title("🖼️ WordPress Image Checker with Google Drive")
wp_url = st.text_input("Paste the WordPress post URL here:")
drive_folder_id = st.text_input("Paste your Google Drive folder ID here:")

# 2. Get WordPress images
def extract_filenames_from_post(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        featured = soup.find("meta", property="og:image")
        featured_src = featured["content"] if featured else ""

        images = soup.find_all("img")
        filenames = [img["src"].split("/")[-1] for img in images if img.get("src")]

        return filenames
    except Exception as e:
        st.error(f"Error extracting images: {e}")
        return []

# 3. Authenticate and connect to Google Drive
def authenticate_google_drive():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": st.secrets["google"]["client_id"],
                        "client_secret": st.secrets["google"]["client_secret"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [st.secrets["google"]["redirect_uri"]],
                    }
                },
                scopes=["https://www.googleapis.com/auth/drive.readonly"],
                redirect_uri=st.secrets["google"]["redirect_uri"],
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.write("👉 [Click here to authorize Google Drive access](%s)" % auth_url)
            code = st.text_input("Paste the full URL after authorizing:")
            if code:
                flow.fetch_token(authorization_response=code)
                creds = flow.credentials
                with open("token.pkl", "wb") as token:
                    pickle.dump(creds, token)
    return creds

# 4. Get file names from Drive folder
def get_filenames_from_drive_folder(folder_id, creds):
    try:
        service = build("drive", "v3", credentials=creds)
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="files(name)"
        ).execute()
        return [f["name"] for f in results.get("files", [])]
    except Exception as e:
        st.error(f"Error accessing Google Drive: {e}")
        return []

# MAIN FUNCTION
if wp_url and drive_folder_id:
    st.info("⏳ Getting image filenames from the WordPress post...")
    post_filenames = extract_filenames_from_post(wp_url)
    st.success(f"✅ Found {len(post_filenames)} image(s) in the post.")

    st.info("🔐 Checking Google Drive permissions...")
    creds = authenticate_google_drive()

    if creds:
        st.info("📁 Reading your Google Drive folder...")
        drive_filenames = get_filenames_from_drive_folder(drive_folder_id, creds)

        st.subheader("🔍 Comparison Results:")
        for name in post_filenames:
            if name in drive_filenames:
                st.success(f"{name} ✔ Found in Drive")
            else:
                st.error(f"{name} ✘ Missing in Drive")
