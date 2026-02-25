import requests
import config
import time

def convert_address(old_address, retries=2):
    headers = {'x-api-key': config.API_KEY_CONVERT, 'Content-Type': 'application/json'}
    payload = {"address": old_address}
    
    for i in range(retries + 1):
        try:
            start_time = time.time()
            response = requests.post(config.URL_CONVERT, json=payload, headers=headers, timeout=30)
            response_time = time.time() - start_time
            response.raise_for_status()
            result = response.json()
            result['response_time'] = round(response_time, 2)
            return result
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            if i < retries:
                time.sleep(1)
                continue
            print(f"API Error {old_address}: {e}")
    return None