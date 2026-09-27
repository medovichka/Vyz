import old.retrieve as retrieve
from config import MY_IP
from DTO import geodata

def get_geo(ip: str) -> list[str] | None:

    info = retrieve.get_data(f"http://ip-api.com/json/{ip}?fields=16592")
    city=info['city']
    coords=f"{info['lat']},{info['lon']}"
    return(city,info['lat'],info['lon'])

if __name__=="__main__":
    print(get_geo(MY_IP))