from youtubesearchpython import VideosSearch
from pprint import pprint as pp
from Video import *
from pytube import YouTube
import os
from algo import *
class FileSizeOver(Exception):
	pass

def getListVideo(kw, page):
    n = 4
    engine = VideosSearch(kw, limit=8)
    listVideo = []
    # pp(engine.result()['result'])
    for video in engine.result()['result']:
        if 'duration' in video:
            if video['duration'] != None: 
                # listVideo.append(Video.fromJson(video))
                listVideo.append({
                    'title': video['title'],
                    'url': video['link'],
                    'viewCount': video['viewCount'],
                    'thumbnail': video['thumbnails'][0]['url'],
                    'publishedTime':video['publishedTime'],
                    'duration': video['duration']
                    })
    return show(listVideo, page, n)

def downloadVideo(url, filename) -> str:
    print(url)
    yt = YouTube(url)
    # t = yt.streams.filter(only_audio=True).all()
    ite = yt.streams
    # try:
    st = next(yt.streams)
    # pp(list(t))
    print('filesize', st.filesize)
    if st.filesize > 25_000_000:
        raise FileSizeOver("File is over than 25mb")
    return st.download(filename=filename)
# pp(getListVideo('chris tomlin'))
def downloadAudio(url, filename):
    print(url)
    yt = YouTube(url)
    st = yt.streams.filter(only_audio=True)
    # print(st)
    pp(st)
    st = st[0]
    # # st = yt.streams.first()
    # # pp(list(t))
    print('filesize', st.filesize)
    if st.filesize > 25_000_000:
        raise FileSizeOver("File is over than 25mb")
    st.download(filename=filename)
    os.rename(f'{filename}.mp4', f'{filename}.mp3')
    

# downloadAudio('https://www.youtube.com/watch?v=LV95aCwGswM', 'audio')
# downloadAudio()

# # from _future_ import unicode_literals
# import youtube_dl
# # from moviepy.editor import *
# import os



# ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
# ydlaudio = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
# def find_ydl_url(url):
#     print("ICI C Ligne 10 find_ydl_url")
#     with ydl:
#         result = ydl.extract_info(
#             url,
#             download=False # We just want to extract the info
#         )

#     if 'entries' in result:
#         video = result['entries'][0]
#     else:
#         video = result
#     pp(video['formats'])
#     video_urls = video['formats']
#     for video_url in video_urls:
#         if video_url['format_id'] == '18' :
#             print('=================================== 360 P ====================================')
#             print('Extension : {}'.format(video_url['ext']))
#             print('URL : {}'.format(video_url['url']))
#             print('Fomart ID: {}'.format(video_url['format_id']))
#             print('Fomart : {}'.format(video_url['format']))
#             print('Filesize : {}'.format(video_url['filesize']))
#             print('=================================== 360 P ====================================')
#             return video_url
# find_ydl_url('https://youtu.be/IHNzOHi8sJs')
# rslt = getListVideo('Blackpink')
# downloadVideo(rslt[0].url)