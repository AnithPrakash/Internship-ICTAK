import gradio as gr
from video_download_and_subtitle import path_and_data
from text_and_summarized import text_and_summarize
from video_scene_detection import merge_and_path


def main(url, progress=gr.Progress()):
    progress(0, desc="Downloading video...")
    download_path, data = path_and_data(url)

    progress(0.3, desc="Generating key points...")
    clip_list, key_points = text_and_summarize(download_path=download_path, data=data)

    progress(0.7, desc="Merging clips...")
    path = merge_and_path(download_path=download_path, data=data, clip_list=clip_list)

    progress(1, desc="Done! 🎉")

    # Format key points nicely in Markdown
    keypoints_md = "\n".join(f"- {point}" for point in key_points)
    return path, keypoints_md


with gr.Blocks(title="🎬 YouTube Video Summarizer") as demo:
    gr.Markdown("## 🎥 YouTube Video Summarizer\nEnter a YouTube URL to extract highlights and key points.")

    url_input = gr.Textbox(label="Enter YouTube URL")

    # Vertical layout
    video_out = gr.Video(label="Processed Video")
    keypoints_out = gr.Markdown(label="Key Points")

    analyze_btn = gr.Button("Analyze Video 🎬")

    # Connect button → function → outputs
    analyze_btn.click(
        fn=main,
        inputs=url_input,
        outputs=[video_out, keypoints_out]
    )

demo.launch(share=True)

