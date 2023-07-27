import requests
import subprocess
import json
import os
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from moviepy.editor import *
 
from pytube import YouTube
import random
 
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip #herere!
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import traceback
from urllib.parse import urljoin

from yt_dlp import YoutubeDL
import threading

 

#Downloads a single youtube video from videourl to save_path.
def download_yt_vid(videourl, save_path):
   
    ydl_opts = {
        'quiet' : True,
        'no_warnings': True,
        'logger' : None,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl' : save_path,
    }
    #'quiet', 'no_warnings', and 'logger' suppresses output from ydl
    # use 'outtmpl': 'C:/Users/raoj6/Videos/Youtube Downloads/Good Processed/%(title)s.%(ext)s', to have the name of the file be the same as video file name.

    with YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(videourl, download=False)
        video_duration = video_info.get('duration')


        MAX_VID_DURATION = 120333
        if(video_duration < MAX_VID_DURATION):
            ydl.download(videourl) 
            print(f"Video {videourl} successfully downloaded.") 
        else:
            print(f"Skipping download for {videourl}. Video length of {video_duration}s exceeds maximum of {MAX_VID_DURATION}s.")

 
#ChannelURL, path of folder to download channel to, prevent_duplicates skips downloading of duplicates
def download_yt_channel(channelURL, folder_path, prevent_duplicates = True): #downloads an entire youtube chanenl to folder path
    URL_array = get_channel_vids(channelURL)
    
    count = 1
    length = len(URL_array)
    for URL in URL_array:
        

        if(prevent_duplicates == True):
            videourl = URL.replace("/","").replace(":","")
            #When we download, we convert videourl just like this ^. So therefore 
            #When we search for it, we have todo this as well.

            file_save_path  = f"{folder_path}/{videourl}.mp4"
            if( f"{videourl}.mp4" in os.listdir(folder_path)):
                print(f"File name |{videourl}.mp4| already exists in folder {folder_path}. Skipping Download.")
            else:
                try:
                    download_yt_vid(URL, file_save_path)
                except Exception as e:
                    #print(f"Error: {e}.")
                    print(f"Error: {e}. {traceback.format_exc()}")

        else:
            try:
                download_yt_vid(URL, file_save_path)
            except Exception as e:
                #print(f"Error: {e}.")
                print(f"Error: {e}. {traceback.format_exc()}")

        print(f"{count} of {length} videos downloaded. \n")
        count = count + 1

def find_all(a_str, sub): #finds all index occurences of 'sub' in 'a_str'
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches
        
def get_channel_vids(URL, scroll_interval = 0.2, iterations =1): #gets urls of all youtube shorts of a channel url. returns list of urls
    
    URL_arrays = []
    for count in range(iterations):
        ##### Web scrapper for infinite scrolling page #####
        driver = webdriver.Chrome(executable_path=r"E:\Chromedriver\chromedriver_win32_chrome83\chromedriver.exe")
        driver.get(URL)
        time.sleep(2)  # Allow 2 seconds for the web page to open
        scroll_pause_time = 0.2 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
        screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web

        
        #click on sort by popular
        driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[1]/ytd-feed-filter-chip-bar-renderer/div/div[3]/iron-selector/yt-chip-cloud-chip-renderer[2]/yt-formatted-string').click()

        i=0
        scroll_heights = []
        while True:
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
            # scroll one screen height each time
            i = i + 1
            time.sleep(scroll_pause_time)
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = driver.execute_script("return document.documentElement.scrollHeight")  #basically represents how much we have scrolled
            scroll_heights.append(scroll_height)
            # Break the loop when the height when we reach the end(which is when the scroll_height stays constant)

            if(i>5): #
                if(scroll_heights[i-1] == scroll_heights[i-5-1]):#checks if the scrollheight has stopped changing (i.e. checks if we ve scrolled to the end
                    break
            
        ##### the actual URLs #####
        urls = []
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for parent in soup.find_all(class_="style-scope ytd-rich-grid-slim-media"):
            a_tag = parent.find("a", class_="yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-slim-media")
            
        
            try:
                link = a_tag.attrs['href']

                fullURL = rf"https://www.youtube.com{link}"
                if(fullURL not in urls):
                    if(len(urls)>0):
                        if(urls[-1] != fullURL):
                            urls.append(fullURL)
                            #print(fullURL)
                    else:
                        urls.append(fullURL)
            except Exception as e:
                #print(e)
                pass
            
        print(f"Iteration {count} obtained {len(urls)} videos.")
        URL_arrays.append(urls)


    return_array = []
    i=0
    while(i< iterations):
        for url in URL_arrays[i]:
            if(url not in return_array):
                return_array.append(url)
        i = i + 1
        
                
    
    return return_array

def cli_loop():
    video_folder_path = os.path.expanduser("~") + "\\Videos"
    video_folder_path = input(f"Enter folder to store downloaded videos in. Press enter to use {video_folder_path}. ")
    if(os.path.exists(video_folder_path) == False):
        video_folder_path = os.path.expanduser("~") + "\\Videos"
    


    command = input("Enter link to youtube video/channel. Enter 'quit' to quit.")
    while( ("quit" in command) ==False):
        if('youtube' in command):

            if (r'youtube.com/channel/' in command or '@' in command or 'youtube.com/c/' in command):
                #We are downloading a channel.
                download_yt_channel(command, video_folder_path)
            else:
                #We are downloading a single video.
                download_yt_vid(command, video_folder_path)
        else:
            print("Please enter valid URL.")
        command = input("Enter command: ")

        

    print("Program exiting...")
    time.sleep(1.5)

def remove_duplicates(vids):
    i=0
    len_vids = len(vids)

    while(i<len_vids):
        if(vids[i] in vids[0:i-1]):
            print(f"popped {vids[i]}")
            vids.pop(i)
            len_vids= len_vids-1

        i= i+1
 
    return vids
 
 

def download_yt_channel_threading(channelURL, folder_path, prevent_duplicates = True):
    URL_array = get_channel_vids(channelURL, iterations=3)

    
    if os.path.exists(folder_path) == False:
        os.mkdir(folder_path)


    threads = []


    for URL in URL_array:
        

        if(prevent_duplicates == True):
            videourl = URL.replace("/","").replace(":","")
            #When we download, we convert videourl just like this ^. So therefore 
            #When we search for it, we have todo this as well.

            file_save_path  = f"{folder_path}/{videourl}.mp4"
            if( f"{videourl}.mp4" in os.listdir(folder_path)):
                print(f"File name |{videourl}.mp4| already exists in folder {folder_path}. Skipping Download.")
            else:
                thread = threading.Thread(target = download_yt_vid, args= (URL, file_save_path,))
                threads.append(thread)

        else:
            thread = threading.Thread(target = download_yt_vid, args= (URL, file_save_path,))
            threads.append(thread)

    

    for thread in threads:
        thread.start()


    for thread in threads:
        thread.join()
    
    #All threads finished

    downloaded_files = os.scandir(folder_path)
    for filename in downloaded_files:
        if('part' in filename.name or 'ytdl' in filename.name):
            os.remove(filename.path)





if __name__ == '__main__':
    downloaded_files = os.scandir(r'C:\Users\raoj6\Videos\Youtube Downloads\Good Unprocessed\Kd_unite')
    for filename in downloaded_files:
        if('part' in filename.name or 'ytdl' in filename.name):
            os.remove(filename.path)


    channels = [
 
   
  
    r'https://www.youtube.com/@Cat-James/shorts',
    r'https://www.youtube.com/@petlover351/shorts', 
    r'https://www.youtube.com/@MaltipooVip/shorts',
    r'https://www.youtube.com/@Corgi_Maks/shorts']

    # channels = [
    # r'https://www.youtube.com/@bellaandquantas/shorts',
    # r'https://www.youtube.com/@Akay_1999/shorts',
    # r'https://www.youtube.com/@vickynga/shorts',
    # r'https://www.youtube.com/@Kd_unite/shorts',
    # r'https://www.youtube.com/@kittyear/shorts',
    # r'https://www.youtube.com/@withmycat2111/shorts',
    # r'https://www.youtube.com/@Cat-James/shorts'
    # r'https://www.youtube.com/@petlover351/shorts', 
    # r'https://www.youtube.com/@MaltipooVip/shorts',
    # r'https://www.youtube.com/@Corgi_Maks/shorts']

    for channel in channels:
        name = channel[channel.index('@')+1: -7]
        download_yt_channel_threading(channel, rf'C:\Users\raoj6\Videos\Youtube Downloads\Good Unprocessed\{name}')

    # download_yt_channel_threading(r'https://www.youtube.com/@bellaandquantas/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@Akay_1999/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@vickynga/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@Kd_unite/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@kittyear/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@withmycat2111/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@Cat-James/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@petlover351/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@MaltipooVip/shorts'
    # download_yt_channel_threading(r'https://www.youtube.com/@Corgi_Maks/shorts'

    # download_yt_vid(r'https://www.youtube.com/watch?v=RoY9DRdzX6g',r'C:\Users\raoj6\Downloads\fellas')
    # download_yt_vid(r'https://www.youtube.com/watch?v=l3k_r56floA',r'C:\Users\raoj6\Downloads\fellas')
    #download_yt_channel_threading(r'https://www.youtube.com/@jtbcatsplus/shorts', r'C:\Users\raoj6\Videos\Youtube Downloads\Good Unprocessed\jtbcatsplus')