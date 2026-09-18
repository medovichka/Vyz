import requests
def get_data(API_URL: str):

    response = requests.get(f"{API_URL}")
    data = response.json()
    return data

def test_data(API_URL: str):

    response = requests.get(f"{API_URL}")
    data = response.json()
    print(f"{response.status_code}\n{data}")

if __name__ == "__main__":
    from config import API_URL
    test_data(API_URL=API_URL)