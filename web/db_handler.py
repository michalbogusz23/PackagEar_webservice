from flask import session
import uuid
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

def save_package(package):
    package_id = str(uuid.uuid4())

    login = session["user"]

    db.hmset(f"package:{login}:{package_id}", package)

    return True
    
def get_packages():
    packages = []

    login = session["user"]
    keys = db.keys(pattern=f"package:{login}*")
     
    for key in keys:
        package = db.hgetall(key)
        package = decode_redis(package)
        package["id"] = key.decode().split(":")[2]
        packages.append(package)

    return packages

def delete_package_from_db(id):
    login = session["user"]
    key = f"package:{login}:{id}"

    db.delete(key)

    return True

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