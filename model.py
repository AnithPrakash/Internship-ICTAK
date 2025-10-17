from video_download_and_subtitle import path_and_data
from text_and_summarized import text_and_summarize
from video_scene_detection import merge_and_path

def main(url):
    download_path, data=path_and_data(url)
    print("\n\n")

    clip_list, key_points=text_and_summarize(download_path=download_path, data=data)
    print("\n\n")

    path=merge_and_path(download_path=download_path,data=data, clip_list=clip_list)
    print("Done This 😊!!!!!!!!")
    return path



if __name__=="__main__":
    main(url="https://youtu.be/eCR17sBh-Qw?si=d6oKHOthn-CMc99Z")