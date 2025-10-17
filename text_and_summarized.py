# Library for the checking the summarization and similarity
from sentence_transformers import SentenceTransformer, util
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd


# Calling the models
summarizer= pipeline("summarization")
nltk.download('punkt_tab')
nltk.download('punkt')

#Load a pre-trained sentence embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')



from video_download_and_subtitle import path_and_data
#download_path, data=path_and_data()



def table_to_paragraph(data):
  """
  Changing the DataFrame into paragragh

  data: Pass the Data Table contain the start, end , text

  """
  text_list=data['text']
  for i in text_list:
    paragraph=" ".join(data["text"])
  return paragraph


def chunk_text(text, max_chunk_length=1000):
    """ RUN INSIDE"""
    # Split text into chunks of max_chunk_length characters
    return [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]


def summarize(text, max_length=80, min_length=50):
    """
    Text : The Long text of paragraph of data

    max_lenght : Max lenght of the summarized text

    min_lenght : MIn lenght of the summarized text

    Changing the long text into the important point to know
    """
    chunks = chunk_text(text)
    summaries = []

    for chunk in chunks:
        result = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        if result and isinstance(result, list):
            summaries.append(result[0]['summary_text'])

    return " ".join(summaries)



def encode(text, table):
  """
  text : The summarized sentence

  table : Pass the Data Table contain the start, end , text

  """
  key_embeddings = model.encode(text, convert_to_tensor=True)
  data_embeddings=model.encode(table['text'].tolist(), convert_to_tensor=True)
  key_index=[]
  for key_emb in key_embeddings:
    similarities=util.cos_sim(key_emb, data_embeddings)[0]
    best_match= torch.argmax(similarities).item()
    key_index.append(best_match)
  return key_index



def keyword_for_unboxing(data):
  """
  data : Pass the Data Table contain the start, end , text

  finding the presence of the keywords in the video for unboxing n'll.
  """
  key_index=[]
  keywords=["unbox", "box", "open the box", "take out", "out of the box",
            "final", "verdict", "recommend", "don't buy", "buy", "overall",
            "conclusion", "impression","price",  "Unboxing experience","First impressions",
            "What’s in the box","Fresh out of the box","Sealed package","Brand new device",
            "Hands-on review","Initial setup","Quick look","Tech unboxing",]
  keywords_lower=[kw.lower() for kw in keywords]
  for index, sentence in data['text'].items():
    if any(kw in sentence.lower() for kw in keywords_lower):
      key_index.append(index)
  return key_index





def key_fact_of_video(paragraph):
  """
  paragraph : summarized paragraph having the key facts

  sort of find the right things for the short clip video
  Most of time half of the paragraph is relevant
  """
  sentence=[s.strip() for s in paragraph.split(".") if s.strip()]

  core_keywords=tech_keywords = [
    # Display
    "display", "screen", "panel", "display quality", "display resolution", "brightness", "nits",
    "contrast ratio", "color accuracy", "HDR", "HDR10", "Dolby Vision", "refresh rate", "adaptive refresh rate",
    "variable refresh rate", "hz", "OLED", "AMOLED", "Super AMOLED", "Retina display", "LTPO", "LCD",
    "mini-LED", "micro-LED", "touchscreen", "edge-to-edge display", "bezel", "always-on display",
    "gorilla glass", "anti-glare", "display protection",

    # Camera
    "camera", "megapixel", "rear camera", "front camera", "selfie", "ultrawide", "telephoto", "macro",
    "depth sensor", "aperture", "OIS", "EIS", "stabilization", "AI camera", "portrait mode", "night mode",
    "HDR photo", "zoom", "optical zoom", "digital zoom", "camera test", "video recording", "slow motion",
    "4K video", "8K video", "capture",

    # Battery & Charging
    "battery", "battery life", "battery backup", "fast charging", "wireless charging", "reverse charging",
    "charging speed", "USB-C charging", "power adapter", "wattage", "battery test", "endurance", "charger",
    "battery health",

    # Performance
    "processor", "chip", "chipset", "GPU", "CPU", "AI engine", "NPU", "performance", "benchmark",
    "gaming benchmark", "fps", "cooling system", "thermal management", "multitasking", "RAM", "ROM",
    "storage", "SSD", "HDD", "expandable storage", "performance test", "app load time", "boot-up speed",
    "heat dissipation",

    # Design & Build
    "design", "build quality", "build and design", "weight", "thickness", "material", "finish",
    "aesthetics", "color options", "ergonomics", "durability", "water resistance", "dust resistance",
    "IP rating", "2-in-1 convertible", "hinge", "keyboard feel", "trackpad response", "port selection",

    # Audio
    "speaker", "stereo speakers", "Dolby Atmos", "Hi-Res audio", "sound quality", "bass", "treble",
    "volume", "microphone", "audio jack", "bluetooth audio", "codec", "media playback",

    # Connectivity
    "USB", "USB-C", "Thunderbolt", "Wi-Fi", "Wi-Fi 6", "Wi-Fi 7", "Bluetooth", "Bluetooth 5.3",
    "NFC", "GPS", "cellular", "5G", "4G", "dual SIM", "eSIM", "port selection",

    # Security
    "fingerprint sensor", "face unlock", "security", "privacy", "biometrics", "encryption", "screen lock",

    # Software
    "Android", "iOS", "UI", "user interface", "software update", "custom skin", "OS version", "bloatware",
    "app performance", "productivity test", "multimedia experience", "Android setup", "iOS setup",

    # Price & Verdict
    "deal", "price", "offer", "value for money", "recommend", "final verdict", "conclusion",
    "overall impression", "buy", "don't buy", "compare", "comparison", "flagship phone", "midrange",
    "budget", "premium"
    ]

  core_keyword_sentence=[
    s for s in sentence
    if any(kw.lower() in s.lower() for kw in core_keywords)]

  return core_keyword_sentence

def text_and_summarize(download_path, data):
   """
   download path :- The download path of the video 

   data :- The data of the text (table of data)

   This function helps to summarize the text and take the key point from the 
    data

    returns :- clip list and the text of key points  
   """
   paragraph=table_to_paragraph(data)
   unboxing=keyword_for_unboxing(data)
   summary=summarize(paragraph)
   text=key_fact_of_video(summary)
   clip_list=encode(text,data)
   clip_list=clip_list+unboxing
   return clip_list, text


if __name__=="__main__":
   download_path, data=path_and_data()
   print("Step 1: Converting transcript table to paragraph...")
   paragraph=table_to_paragraph(data)
   print(f"✅ Done: Paragraph generated\n {paragraph}")

   print("Step 2 : Finding the unboxing part")
   unboxing=keyword_for_unboxing(data)
   print(f"✅ Done: Unboxing \n {unboxing}")

   print("Step 3: Summarizing paragraph...")
   summary=summarize(paragraph)
   print(f"✅ Done: Summary complete\n {summary}")

   print("Step 4 : Finding the key facts")
   text=key_fact_of_video(summary)
   print(f"✅ Done: found the facts {text}")

   print("Step 5: Encoding summary into clip list...")
   clip_list=encode(text,data)
   clip_list=clip_list+unboxing
   print(f"✅ Done: Clip list encoded\n {clip_list}")
  