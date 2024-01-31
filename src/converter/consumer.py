import pika, sys, os, time
from convert import to_mp3
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo import MongoClient 
import gridfs

def main():
    mongo_client = MongoClient("host.minikube.internal", 27017 )

    video_db = mongo_client.videos
    mp3_db = mongo_client.mp3s

    fs_videos = gridfs.GridFS(video_db)
    fs_mp3s = gridfs.GridFS(mp3_db)

    connection = pika.BlockingConnection([pika.ConnectionParameters(host="rabbitmq")])
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)




# def main():
#     mongo_client = AsyncIOMotorClient("mongodb://host.minikube.internal:27017")
#     video_db = mongo_client.videos
#     fs_videos = AsyncIOMotorGridFSBucket(video_db)
#     # (video_db)
    
#     mp3_db = mongo_client.mp3
#     fs_mp3s = AsyncIOMotorGridFSBucket(mp3_db)
    
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
#     channel = connection.channel()

#     def callback(ch, method, properties, body):
#         err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
#         if err:
#             ch.basic_nack(delivery_tag = method.delivery_tag)
#         else:
#             ch.basic_ack(delivery_tag = method.delivery_tag)


#     channel.basic_consume(queue = os.environ.get("VIDEO_QUEUE"), on_message_callback = callback)

#     print("Waiting for message. CTRL+c to exit.")
    
#     channel.start_consuming()

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("Interrupted")
#         try:
#             sys.exit(0)
#         except SystemExit:
#             os._exit(0)
