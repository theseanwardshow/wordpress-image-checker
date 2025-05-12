import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("🖼️ WordPress Image Checker")

# Step 1: User enters a WordPress post URL
wp_url = st.text_input("Paste the WordPress post URL here:")

if wp_url:
    try:
        # Step 2: Fetch and parse the page
        response = requests.get(wp_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Step 3: Find the featured image and skip it
        featured_image = soup.find("meta", property="og:image")
        featured_src = featured_image["content"] if featured_image else ""

        # Step 4: Extract all other <img> tags
        images = soup.find_all("img")
        other_images = [img for img in images if img.get("src") != featured_src]

        # Step 5: Get just the filenames
        filenames = [img["src"].split("/")[-1] for img in other_images if img.get("src")]

        st.write("🔍 Found the following image files in the post:")
        for name in filenames:
            st.write("•", name)

        # Step 6: Upload folder content manually (for now)
        st.markdown("---")
        st.subheader("📁 Upload Google Drive filenames list")
        uploaded_file = st.file_uploader("Upload a .txt or .csv file with Google Drive filenames", type=["txt", "csv"])

        if uploaded_file:
            drive_filenames = [line.strip() for line in uploaded_file.readlines()]
            st.markdown("---")
            st.subheader("✅

            for name in filenames:
                if name in drive_filenames:
                    st.success(f"{name} ✔ Found in Google Drive list")
                else:
                    st.error(f"{name} ✘ Not found in Google Drive list")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
