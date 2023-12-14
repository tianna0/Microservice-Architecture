import pika, json


def upload(f, fs, channel, access):
    """upload file to mongodb using gridfs
        once uploaded, put a message in rabbitmq
    """
    try:
        fid = fs.put(f) #put file in mongodb
    except Exception as err:
        print(err)
        return "internal server error", 500

    
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    #put message on rabbitmq
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print(err)
        fs.delete(fid)
        return "internal server error", 500