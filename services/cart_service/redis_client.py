import redis
import json
import time
import random
from datetime import datetime
import requests

# Connect to Redis server
redis_host = 'localhost' 
redis_port = 6379  
redis_password = "redisP@ssw0rd"  
# Se crea el cliente
redis_client = redis.Redis(host=redis_host, 
                           port=redis_port, 
                           password=redis_password)

list_name = 'communications_logs_queue'
def push_to_list(item):
    redis_client.rpush(list_name, item)

def send_request_info(requestInfo):
    push_to_list(json.dumps(requestInfo))

def track_request(caller_service_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            response = func(*args, **kwargs)  
        
            # Calculate latency in milliseconds
            latency_ms = (time.time() - start_time) * 1000
            
            receiver_service_id = kwargs.get('receiver_service_id', None)
            # Check if the response is a `requests.Response` object
            if isinstance(response, requests.Response):
                request_info = {
                    'datetime': current_datetime,
                    'caller_service_id': caller_service_id,
                    'receiver_service_id': receiver_service_id,
                    'status_code': response.status_code,
                    'latency_ms': int(latency_ms)
                }
                # Call your existing Redis handling function
                send_request_info(request_info)
                print(f"Logged to Redis: {request_info}")
            
            return response
        return wrapper
    return decorator

def track_fake_request(caller_service_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            response = func(*args, **kwargs)  
            print("responsee ", response)
            time.sleep(0.009*random.random())
            latency_ms = (time.time() - start_time) * 1000
            
            receiver_service_id = kwargs.get('receiver_service_id', 8)
            fake_status_code = kwargs.get('fake_status_code', 200)
            request_info = {
                'datetime': current_datetime,
                'caller_service_id': caller_service_id,
                'receiver_service_id': receiver_service_id,
                'status_code': fake_status_code,
                'latency_ms': int(latency_ms)
            }
            send_request_info(request_info)
            print(f"Logged to Redis: {request_info}")
            
            return response
        return wrapper
    return decorator

@track_request(caller_service_id=2)
def make_api_get_request(url, json=None, params=None, receiver_service_id=None):
    response = requests.get(url, json=json, params=params)
    response.raise_for_status()
    return response

@track_request(caller_service_id=2)
def make_api_post_request(url, params=None, receiver_service_id=None):
    response = requests.post(url, json=params)
    response.raise_for_status()
    return response

@track_fake_request(caller_service_id=2)
def make_fake_request(receiver_service_id=None, fake_status_code=None):
    return "response"
# # Uso de ejemplo
# if __name__ == "__main__":
#     example_requests = [ {'datetime':'2024-02-19 5:00:00',
#                           'caller_service_id': 4,
#                           'receiver_service_id': 1,
#                           'status_code': 202,
#                           'latency_ms': 100}, 
#                         ]

#     for request in example_requests:
#         #json dumps convierte de diccionario a string
#         push_to_list(json.dumps(request))

#     print(f"Información enviada exitosamente a la lista {list_name}.")