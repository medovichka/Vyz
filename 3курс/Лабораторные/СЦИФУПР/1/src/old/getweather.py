from config import API_KEY, MY_IP
import old.retrieve as retrieve
import old.getip as getip

WEATHER_API_KEY=API_KEY
IP=MY_IP
city,lat,lon = getip.get_geo(IP)

def get_weather_point(lat,lon,API_KEY):
    weather_point = retrieve.get_data(API_URL=f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru")
    return weather_point

if __name__=="__main__":
    city,lat,lon = getip.get_geo(IP)
    print(get_weather_point(lat,lon,API_KEY=WEATHER_API_KEY))