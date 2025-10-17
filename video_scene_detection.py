# Library to import for the ContentDetection
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy import VideoFileClip

#Library for concating the video
from moviepy import VideoFileClip, concatenate_videoclips
from scenedetect import FrameTimecode

#Library needed for the scenedetection
import scenedetect
from scenedetect import open_video
from scenedetect import detect, ContentDetector, split_video_ffmpeg

#Common Library 
import pandas as pd
from IPython.display import Video, display
from datetime import datetime
from typing import Dict, List
import os



from video_download_and_subtitle import path_and_data
from text_and_summarized import text_and_summarize



def scene_detected(path:str)-> str:
  """
  path : The Path of the download video

  Help to detected the scene in the video
  """
  scenes=detect(path, ContentDetector())
  data=[]
  for (scene_start, scene_end) in scenes:
    data.append({"Scene_start":scene_start, "Scene_end":scene_end})
  show_data=pd.DataFrame(data)
  return data, show_data


def select_row(data, clip_list):
  """
  data : Pass the Data Table contain the start, end , text

  clip_list : The list of index that have the important content
  """
  cols=["start","end"]
  result = [x - 1 for x in clip_list]
  selected_rows=data.iloc[result][cols]
  return selected_rows


def overlapping(select_row,list):
  """
  select_row : The selected row table contain the start and end

  list : The index of the key fact sentence

  """
  data=select_row.sort_values(by="start").reset_index(drop=True)
  non_overlapping=[]
  last_end= -float("inf")

  for _, row in data.iterrows():
    if row['start'] >= last_end:
      non_overlapping.append(row)
      last_end= row["end"]

  return pd.DataFrame(non_overlapping)




def time_to_seconds(time_str):
    """
    RUN INSIDE
    Converts HH:MM:SS or HH:MM:SS.mmm to total seconds safely.
    """
    import re

    # Extract numbers
    parts = re.split('[:.]', time_str)
    parts = [float(p) for p in parts if p.strip() != '']

    # Handle missing parts (like MM:SS)
    while len(parts) < 3:
        parts.insert(0, 0.0)

    h, m, s = parts[:3]

    # Fix invalid values
    if s >= 60:
        s = 59.999
    if m >= 60:
        m = 59

    return h * 3600 + m * 60 + s



def matchingScene(selected_rows,scene_data):
  """
  selected_rows : The index and the start/end time of video imp

  scene_data : The detect scene from the video
  """
  scene_start_seconds=[time_to_seconds(str(scene["Scene_start"])) for scene in scene_data]
  matching_indices=[]
  for start_time in selected_rows['start']:
    closed_index=min(range(len(scene_start_seconds)), key=lambda i: abs(scene_start_seconds[i] - start_time))
    matching_indices.append(closed_index)
  return matching_indices


from typing import Dict, List
def merge_video(data=List[Dict],path=str,clip=list):
  """
  data: The List of start and end point of scenedetection

  path: Path of the video

  clip[List]: The list of scene need to be merge

  """

  clip_path=VideoFileClip(path)
  split_clips=[]

  for arg in clip:
    scene=data[arg]
    start_tc=scene["Scene_start"]
    end_tc=scene["Scene_end"]

    start_sec=start_tc.get_seconds()
    end_sec=end_tc.get_seconds()

    split_clips.append(clip_path.subclipped(start_sec, end_sec))

  final_clip=concatenate_videoclips(split_clips)
  output_path = os.path.abspath("merge.mp4")
  final_clip.write_videofile(output_path)

  return output_path


def merge_and_path(download_path, data, clip_list):
   """
   download_path :- The download path of the video

   data :- The text table contain the audio transcription 

   clip_list :- The list of clip 

   This function help to download the video and its show the path of the 
   video 

   return :- The path of the video

   """
   scene_detect, show_data=scene_detected(download_path)
   selected_row=select_row(data=data, clip_list=clip_list)
   non_overlapping=overlapping(select_row=selected_row, list=clip_list)
   matched_index=matchingScene(selected_rows=non_overlapping,scene_data=scene_detect)
   path=merge_video(data=scene_detect,path=download_path,clip=matched_index)
   return path



if __name__=="__main__":
    download_path, data=path_and_data()
    clip_list=text_and_summarize(download_path=download_path, data=data)
    print(" \n\n")
    print("Step 1: Detecting scenes...")
    scene_detect, show_data=scene_detected(download_path)
    print(f"✅ Done: Scenes detected\n {scene_detect} \n {show_data}")
    print(" \n\n")
    print("Step 2: Selecting relevant rows...")
    selected_row=select_row(data=data, clip_list=clip_list)
    print(f"✅ Done: Rows selected\n {selected_row}")
    print(" \n\n")
    print("step 3 : Find is there any overlapping")
    non_overlapping=overlapping(select_row=selected_row, list=clip_list)
    print(f"✅ Done: nonoverlapping-Rows selected\n {non_overlapping}")
    print(" \n\n")
    print("Step 4: Matching selected rows to detected scenes...")
    matched_index=matchingScene(selected_rows=non_overlapping,scene_data=scene_detect)
    print(f"✅ Done: Matching complete\n {matched_index}")
    print(" \n\n")
    print("Step 5: Merging video clips...")
    path=merge_video(data=scene_detect,path=download_path,clip=matched_index)
    print(path)
