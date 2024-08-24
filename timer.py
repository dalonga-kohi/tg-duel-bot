import time
import redis
import threading
from config import R_HOST, R_PORT


r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)

def set_timer(seconds, key):
    r.set(key, seconds)

def countdown(seconds, key, next):
    set_timer(seconds, key)
    
    def decrement_time():
        remaining_time = r.get(key)
        if remaining_time:
            remaining_time = int(remaining_time)
            
            if remaining_time > 0:
                r.decr(key)
                print(f"Time remaining: {remaining_time} seconds")
                
                threading.Timer(1, decrement_time).start()
            else:
                next()
                r.delete(key)
        else:
            print("No timer set.")
    
    decrement_time()