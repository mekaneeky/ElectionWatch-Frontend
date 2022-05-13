import requests
def get_url(url):
    try:
        return requests.get(url).json()
    except Exception as e:
        print(e)
        return None