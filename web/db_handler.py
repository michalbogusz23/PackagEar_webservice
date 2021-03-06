import uuid
import sys
from dotenv import load_dotenv
from os import getenv
from redis import StrictRedis

load_dotenv()
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PASS = getenv("REDIS_PASS")
REDIS_INSTANCE = getenv("REDIS_INSTANCE")
db = StrictRedis(REDIS_HOST, db=REDIS_INSTANCE, password=REDIS_PASS)

def is_user(login):
    return db.hexists(f"user:{login}", "password")

def save_label(label, login):
    label_id = str(uuid.uuid4())

    db.hmset(f"label:{login}:{label_id}", label)

    return True
    
def get_user_labels(login):
    labels = []

    keys = db.keys(pattern=f"label:{login}*")
     
    for key in keys:
        label = db.hgetall(key)
        label = decode_redis(label)
        label["id"] = key.decode().split(":")[2]
        labels.append(label)

    return labels

def get_all_labels():
    labels = []

    keys = db.keys(pattern="label:*")
     
    for key in keys:
        label = db.hgetall(key)
        label = decode_redis(label)
        label["id"] = key.decode().split(":")[2]
        label["sender"] = key.decode().split(":")[1]
        labels.append(label)

    return labels

def delete_label_from_db(id, login):
    key = f"label:{login}:{id}"

    db.delete(key)

    return True

def save_package(label_id, status):
    db.hmset(f"package:{label_id}", status)
    return True

def update_package(label_id, status):
    db.hmset(f"package:{label_id}", status)

    return True

def get_all_packages():
    packages = []

    keys = db.keys(pattern="package:*")
    
    for key in keys:
        package = db.hgetall(key)
        package = decode_redis(package)
        print(package, file=sys.stderr)
        package["id"] = key.decode().split(":")[1]
        packages.append(package)

    return packages
    
    # to_delete = db.keys('package:*')
    # print(to_delete, file=sys.stderr)
    # for key in to_delete:
    #     db.delete(key)

    # return True

def decode_redis(src):
    if isinstance(src, list):
        rv = list()
        for key in src:
            rv.append(decode_redis(key))
        return rv
    elif isinstance(src, dict):
        rv = dict()
        for key in src:
            rv[key.decode()] = decode_redis(src[key])
        return rv
    elif isinstance(src, bytes):
        return src.decode()
    else:
        raise Exception("type not handled: " +type(src))

def get_notifications(login):
    msg = db.lpop(f"{login}:notifications")
    if msg:
        return msg.decode()
    return msg

def add_notifications(login, msg):
    return db.lpush(f"{login}:notifications", msg)