from fastapi import FastAPI, Request, HTTPException
import time

request_counters = {} #in mem storage for requests

class RateLimiter:
    def __init__(self, requests_limit, time_window):
        self.requests_limit = requests_limit
        self.time_window = time_window
    
    async def __call__(self, request: Request):
        client_ip = request.client.host 
        route_path = request.url.path 

        cur_time = int(time.time()) #get current timestamp
        #make key for user
        key = f"{client_ip}:{route_path}"

        if key not in request_counters:
            request_counters[key] = {"timestamp": cur_time, "count": 1}
        #if window expired update timestamp
        if cur_time - request_counters[key]["timestamp"] > self.time_window:
            request_counters[key]["timestamp"] = cur_time
            request_counters[key]["count"] = 1
        else: #check if exceeded request limit
            if request_counters[key]["count"] > self.requests_limit:
                raise HTTPException(status_code=429, detail="Too many requests")
            else:
                request_counters[key]["count"] += 1
        return True
