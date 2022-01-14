from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

musicPath = "/home/alberto/Videos/Nier Automata.mp4"
clip = VideoFileClip(musicPath).subclip(17, 19)
clip.write_videofile("/home/alberto/Videos/Nier Automata2.mp4")
