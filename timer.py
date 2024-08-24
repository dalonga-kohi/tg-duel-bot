import time
import redis
import threading
from config import R_HOST, R_PORT


r = redis.Redis(host=R_HOST, port=R_PORT, db=0, charset="utf-8", decode_responses=True)

active_timers = {}

def set_timer(seconds, key):
    r.set(key, seconds)

def countdown(seconds, key, step=None, next=None):
    set_timer(seconds, key)
    
    def decrement_time():
        remaining_time = r.get(key)
        if remaining_time:
            remaining_time = int(remaining_time)
            
            if remaining_time > 0:
                r.decr(key)
                
                if step:
                    step()
                
                active_timers[key] = threading.Timer(1, decrement_time)
                active_timers[key].start()
            else:
                if next:
                    next()
                
                r.delete(key)
                if key in active_timers:
                    del active_timers[key]
        else:
            print("No timer set.")
    
    decrement_time()

def delete_countdown(key):
    if r.exists(key):
        r.delete(key)
        print(f"Timer '{key}' deleted from Redis.")
    else:
        print(f"No timer with key '{key}' found in Redis.")
    
    if key in active_timers:
        active_timers[key].cancel()
        del active_timers[key]
        print(f"Active timer '{key}' stopped.")
    else:
        print(f"No active timer for key '{key}'.")