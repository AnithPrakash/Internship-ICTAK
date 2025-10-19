import streamlit as st
from video_download_and_subtitle import path_and_data
from text_and_summarized import text_and_summarize
from video_scene_detection import merge_and_path

# Page configuration
st.set_page_config(
    page_title="🎬 YouTube Video Summarizer",
    page_icon="🎥",
    layout="centered"
)

# App title and description
st.title("🎥 YouTube Video Summarizer")
st.markdown("Enter a YouTube URL to extract highlights and key points automatically.")

# Input field
url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

# Analyze button
if st.button("🎬 Analyze Video"):
    if not url.strip():
        st.warning("⚠️ Please enter a valid YouTube URL.")
    else:
        try:
            progress_text = st.empty()
            progress_bar = st.progress(0)

            # Step 1: Download video
            progress_text.text("📥 Downloading video...")
            download_path, data = path_and_data(url)
            progress_bar.progress(30)

            # Step 2: Generate key points
            progress_text.text("🧠 Generating key points...")
            clip_list, key_points = text_and_summarize(download_path=download_path, data=data)
            progress_bar.progress(70)

            # Step 3: Merge summarized clips
            progress_text.text("🎞️ Merging clips...")
            path = merge_and_path(download_path=download_path, data=data, clip_list=clip_list)
            progress_bar.progress(100)

            progress_text.text("✅ Done! Video summarized successfully.")

            # Display summarized video
            st.video(path)

            # Display key points
            st.markdown("### 📝 Key Points")
            for point in key_points:
                st.markdown(f"- {point}")

            # Optional download button
            with open(path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Summarized Video",
                    data=f,
                    file_name="summarized_video.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
