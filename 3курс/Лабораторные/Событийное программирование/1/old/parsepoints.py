from old.getweather import get_weather_point
from old.getip import get_geo
from  config import MY_IP,API_KEY
from datetime import date,timedelta,datetime
from DTO import WeatherPoint




def parse_weather() -> list[WeatherPoint]:

    DAYS=[]

    city,latitude,longitude=get_geo(ip=MY_IP)
    list_of_points=get_weather_point(API_KEY=API_KEY,lat=latitude,lon=longitude)["list"]

    today=date.today()
    tomorrow=today + timedelta(days=1)
    zavtrazavtra=tomorrow + timedelta(days=1)

    for day in list_of_points:
        ready_to_save_day = WeatherPoint()
        ready_to_save_day.date=datetime.fromisoformat(day["dt_txt"]).date()
        ready_to_save_day.temperature=day["main"]["temp"]
        ready_to_save_day.temp_min=day["main"]["temp_min"]
        ready_to_save_day.temp_max=day["main"]["temp_max"]
        ready_to_save_day.humidity=day["main"]["humidity"]
        ready_to_save_day.windspeed=day["wind"]["speed"]
        ready_to_save_day.description = day["weather"][0]["description"]
        DAYS.append(ready_to_save_day)
    return DAYS

if __name__ =="__main__":
    parse_weather()