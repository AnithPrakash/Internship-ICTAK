# Library to import for the video download
from pytubefix import YouTube
from pytubefix.cli import on_progress
# Library for the subtitile
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
from pydub import AudioSegment
import pandas as pd
from typing import Dict, List
import os


def download_youtube_video(url:str,filename="Sample.mp4"):
    """
    provide the Url
    """
    try:
        #Asking for the url
        #url=str(input("Enter the url of the video:-  "))
        url=url

        # Create a YouTube object
        yt = YouTube(url)

        # Get the Video
        stream = yt.streams.filter(file_extension="mp4", progressive=True).first()

        # Download the video with a specific filename (if provided)
        if filename:
            downloaded_file = stream.download(filename=filename)
        else:
            downloaded_file = stream.download()

        # Print the name of the downloaded file
        print(f"Video downloaded successfully: {downloaded_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

    return url, downloaded_file




def extract_video_id(url:str):
  """ RUN INSIDE"""
  parsed=urlparse(url)
  if parsed.hostname in {"www.youtube.com","youtube.com"}:
    qs=parse_qs(parsed.query)
    if "v" in qs:
      return qs["v"][0]
  return parsed.path.lstrip("/")



def download_subtitle_or_transcribe(url,download_path):
  """ Try to download the subtitle else audio Transcription

  URL : Pass the Url

  Download_path : Pass the download path of the video
  """
  try:
    video_id=extract_video_id(url)
    ytt_api=YouTubeTranscriptApi()
    subtitle=ytt_api.fetch(video_id)
    data =[{"text": s.text, "start": s.start, "duration": s.duration, "end": s.start + s.duration } for s in subtitle.snippets]
    dataframe=pd.DataFrame(data)
    return dataframe
  except Exception as e:
    video_audio = AudioSegment.from_file(download_path)
    video_audio.export("audio.wav", format="wav")
    model = whisper.load_model("base")
    result = model.transcribe("audio.wav", language="en", verbose=False)
    segments = result["segments"]
    df = pd.DataFrame(segments)
    selected_df = df[['start', 'end', 'text']]
    return selected_df
  

def path_and_data(url):
    """
    This Function ask you to pass the URL and it will 
    automatic download the subtitle or text contained in the video

    return :- download path , data 
    """
    url, download_path=download_youtube_video(url)
    data=download_subtitle_or_transcribe(url=url, download_path=download_path)
    return download_path, data


if __name__=="__main__":
  url, download_path=download_youtube_video(url="https://youtu.be/eCR17sBh-Qw?si=d6oKHOthn-CMc99Z")
  data=download_subtitle_or_transcribe(url=url, download_path=download_path)
  print(f" \nYour downloaded path of the video is {download_path}\n ")
  print(f"The URL of the video you downloaded is {url}\n")
  print(f"The text (audio speech) used in the video in table \n {data}")

   

