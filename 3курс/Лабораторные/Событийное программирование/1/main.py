from api_caller import *
from config import *
from to_md import *
from save import *
from wpp_parser import *

IP = MY_IP
API = API_KEY


if __name__ == "__main__":
    lat, lon = get_geo(IP)
    print("----")
    weather_points_list = get_weather_points(lat=lat, lon=lon, API=API)
    print("----")
    parsed_points = parse_weather(list_of_points=weather_points_list)
    print("----")
    save_points(parsed_points)
    print("----")
    points = load_points()
    points_to_markdown(points=points)
