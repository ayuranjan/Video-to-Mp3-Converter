import pika, json


def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        return "Internal Server Error : File Not Uploaded Sucessfully", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        return "File Successfully Uploaded : Waiting to be processed !" , 200
    except Exception as err:
        fs.delete(fid)
        return "Internal Server Error: File Can not be processed. Upload Again !", 500