import googleapiclient.discovery
import json
import time
import socket
from langdetect import detect

def send_to_logstash(host, port, data):
    error = True
    while error:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket created. sock: " + str(sock))
        
            sock.connect((host, port))
            print("Socket connected to HOST: " + host + " PORT: " + str(port))
            print("Socket connected. Sock: " + str(sock))

            print("Sending message: " + str(data))

            sock.sendall(json.dumps(data).encode())
            print("End connection")
            sock.close()
            error = False
        except:
            print("Connection error. There will be a new attempt in 10 seconds")
            time.sleep(10)


api_key = "AIzaSyDE_pPuZmbdaJkVMbMrNiIZfjqTL2gdi-c"

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

request_videos = youtube.videos().list(
    part="snippet,statistics",
    chart="mostPopular",
    maxResults=200
)

response_videos = request_videos.execute()

popular_videos = response_videos["items"]

logstash_host = "10.0.100.26" 
logstash_port = 9800

for video_info in popular_videos:
    video_id = video_info["id"]
    snippet = video_info["snippet"]
    statistics = video_info["statistics"]

    video_data = {
        "video_id": video_id,
        "title": snippet["title"],
        "channel_title": snippet["channelTitle"],
        "view_count": int(statistics.get("viewCount", 0)),
        "like_count": int(statistics.get("likeCount", 0)),
        "dislike_count": int(statistics.get("dislikeCount", 0)),
        "comment_count": int(statistics.get("commentCount", 0))
    }

    if int(video_data["comment_count"]) > 0:
        request_comments = youtube.commentThreads().list( 
            part="snippet",
            videoId=video_id, 
            maxResults=20,
            order="relevance"
        )

        try:
            response_comments = request_comments.execute()
            comments = [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for item in response_comments["items"]]
            english_comments = [comment for comment in comments if detect(comment) == "en"] 
            video_data["comments"] = english_comments

        except Exception as e:
            print("Error while fetching comments:", e)
            continue


    send_to_logstash(logstash_host, logstash_port, video_data)

    time.sleep(10)
