#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions to communicate with the youtube API
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#For youtube api
#import httplib2
#import six
#from googleapiclient.discovery import build
from apiclient.discovery import build
import sys
import re

from resources.lib import vars
from resources.lib import dev

##### YOUTUBE CONVERTERS #####
#Converts youtube publishedAt date to list containing year, month, day, hour, minutes, seconds
def convert_published(date):
    d = {}
    d['year'] = date[:4]
    d['month'] = date[5:7]
    d['day'] = date[8:10]
    d['hour'] = date[11:13]
    d['minute'] = date[14:16]
    d['second'] = date[17:19]
    return d


##### YOUTUBE API FUNCTIONS #########
#Grabs the Channel information by the playlist ID 
#Returns the channel id 
def yt_get_playlist_info(id):
    #Connect to youtube API
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    #Retrieve the information from the youtube API
    response = youtube.playlists().list(
      part="contentDetails,id,snippet",
      id=id,
      maxResults=50
    ).execute()
    
    return response
    '''
    videos = []
    
    #Grab the playlists from the response
    playlists = search_response['items'][0]['contentDetails']['relatedPlaylists']
    
    # Go through each playlist and display the playlist
    for key, value in playlists.iteritems():
      #videos.append(search_result)
      url = build_url({'mode': 'addPlaylist', 'id': value})
      adddir(key, url, search_response['items'][0]['snippet']['thumbnails']['default']['url'])
    '''


#Grabs the playlists that the given channelid has created
def yt_get_playlists_by_channel(id):
    #Connect to youtube API
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    #Retrieve the information from the youtube API
    response = youtube.playlists().list(
      part="contentDetails,snippet",
      channelId=id,
      maxResults=50
    ).execute()
    
    return response['items']
      


#Grabs playlists & channel information by id
# Params:
    # ChannelId : The id of the channel we want to retrieve
def yt_get_channel_info(Channelid):
    #Connect to youtube API
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    dev.log('GET yt_get_channel_info: https://www.googleapis.com/youtube/v3/channels?part=snippet%2C+contentDetails%2C+brandingSettings&maxResults=50&id='+Channelid+'&key='+vars.API_KEY)

    #Search for the channels with the following parameters
    search_response = youtube.channels().list(
      part="brandingSettings,snippet,contentDetails",
      id=Channelid,
      maxResults=50
    ).execute()
    
    return search_response
      
      
#Searches for channels by keyword
# Params:
    # keyword : The keyword we want to use to search for channels
def search_channel(keyword):
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    search_response = youtube.search().list(
      q=keyword,
      part="id,snippet",
      maxResults=50,
      type = "channel"
    ).execute()
    
    videos = []

    for search_result in search_response.get("items", []):
      #videos.append(search_result)
      url = dev.build_url({'mode': 'pickedChannel', 'id': search_result['id']['channelId']})
      dev.adddir(search_result['snippet']['title'], url, search_result['snippet']['thumbnails']['high']['url'], fanart=search_result['snippet']['thumbnails']['high']['url'], description=search_result['snippet']['description'])

      
#Searches for Youtube videos by a given keyword
# Params:
    # keyword: The keyword to search for
def search_by_keyword(keyword):
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    search_response = youtube.search().list(
      q=keyword,
      part="id,snippet",
      maxResults=50
    ).execute()
    
    for search_result in search_response.get("items", []):
      #videos.append(search_result)
      dev.additem(search_result['snippet']['title'], 'http://somevid.mkv', search_result['snippet']['thumbnails']['default']['url'])

#Grabs the videos from a playlist by playlistId
# Params: 
    # id: The id of the playlist which videos you want to retrieve
    #nextpage: The nextpage token. Default: false. If set it will retrieve the page. That allows all videos to be parsed, instead of the 50 limit
def vids_by_playlist(id, nextpage = False):
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    
    if nextpage == False:
        dev.log('GET vids_by_playlist: https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2C+contentDetails&maxResults=50&playlistId='+id+'&key='+vars.API_KEY)
        search_response = youtube.playlistItems().list(
          part="snippet,contentDetails",
          maxResults=50,
          playlistId=id
        ).execute()
    else:
        dev.log('GET vids_by_playlist: https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2C+contentDetails&maxResults=50&playlistId='+id+'&pageToken='+nextpage+'&key='+vars.API_KEY)
        search_response = youtube.playlistItems().list(
          part="snippet,contentDetails",
          maxResults=50,
          playlistId=id,
          pageToken=nextpage
        ).execute()
    
    return search_response

    # for search_result in search_response.get("items", []):
      # dev.additem(search_result['snippet']['title'], 'http://somevid.mkv', search_result['snippet']['thumbnails']['default']['url'])

#Grabs the duration of a list of youtube video IDs (you can add a max of 50 videoIDs to each call)
def get_duration_vids(vid_ids):
    dev.log('Grabbing duration of youtube videos')
    
    #Create a seperated string of vid_ids to give to the API
    idlist = ''
    for id in vid_ids:
        idlist += id+','
    idlist = idlist[:-1]
    
    youtube = build(
      vars.YOUTUBE_API_SERVICE_NAME, 
      vars.YOUTUBE_API_VERSION, 
      developerKey=vars.API_KEY
    )
    search_response = youtube.videos().list(
      part="contentDetails",
      maxResults=50,
      id=idlist
    ).execute()

    #Get the duration of each video in the response
    durations = {}
    for vid in search_response.get("items", []):      
        dur = vid['contentDetails']['duration']
        dur = dur[2:] #Strip PT from the duration
        #dev.log('Duration of video: '+dur)
        
        seconds = hms_to_sec(dur)

        #dev.log('Which makes the video %s seconds long' % seconds)
        vidid = vid['id']
        durations[vidid] = seconds
        #except Exception as e:
            #dev.log("Couldnt extract time: %s" % e)
            #pass
    
    return durations
    
    
#Recalculates 00h00m00s back to number of seconds
def hms_to_sec(hms):
    m = re.search(r'(?i)((\d+)h)?((\d+)m)?((\d+)s)?', hms)
    if m:
        hours = m.group(2)
        minutes = m.group(4)
        seconds = m.group(6)
        if seconds is None:
            seconds = '0' #Seconds was not set in the setting, so we start with 0 seconds
        seconds = int(seconds)
        #dev.log('Seconds is '+str(seconds))
        if minutes is not None: #If minutes are specified
            #dev.log('minutes is '+minutes)
            sm = int(minutes) * 60
            seconds = seconds + sm
        if hours is not None:
            #dev.log('hours is '+hours)
            sh = int(seconds) * 60 * 60
            seconds = seconds + sh
        return seconds
    else:
        dev.log('Could not extract seconds from hms format: '+hms, True)
        return None
