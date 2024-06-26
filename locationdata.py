# helper functions to use location data
# K7MHI Kelly Keeton 2024

from geopy.geocoders import Nominatim # pip install geopy
import maidenhead as mh # pip install maidenhead
import requests # pip install requests
import bs4 as bs # pip install beautifulsoup4

URL_TIMEOUT = 10 # wait time for URL requests
DAYS_OF_WEATHER = 4 # weather forecast days, the first two rows are today and tonight

def where_am_i(lat=0, lon=0):
    whereIam = ""
    if float(lat) == 0 and float(lon) == 0:
        return "no location data: does your device have GPS?"
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="mesh-bot")

    location = geolocator.reverse(lat + ", " + lon)
    address = location.raw['address']
    address_components = ['house_number', 'road', 'city', 'state', 'postcode', 'county', 'country']
    whereIam += ' '.join([address.get(component, '') for component in address_components if component in address])
    grid = mh.to_maiden(float(lat), float(lon))
    whereIam += " Grid: " + grid

    return whereIam

def get_tide(lat=0, lon=0):
    station_id = ""
    if float(lat) == 0 and float(lon) == 0:
        return "no location data: does your device have GPS?"
    station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/tidepredstations.json?lat=" + str(lat) + "&lon=" + str(lon) + "&radius=50"
    station_data = requests.get(station_lookup_url, timeout=URL_TIMEOUT)
    if(station_data.ok):
        station_json = station_data.json()
        #get first station id in 50 mile radius
        station_id = station_json['stationList'][0]['stationId']
    else:
        return "error fetching station data"

    station_url = "https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=" + station_id
    station_data = requests.get(station_url, timeout=URL_TIMEOUT)
    if(station_data.ok):
        #extract table class="table table-condensed"
        soup = bs.BeautifulSoup(station_data.text, 'html.parser')
        table = soup.find('table', class_='table table-condensed')

        #extract rows
        rows = table.find_all('tr')
        #extract data from rows
        tide_data = []
        for row in rows:
            row_text = ""
            cols = row.find_all('td')
            for col in cols:
                row_text += col.text + " "
            tide_data.append(row_text)
        # format tide data into a string
        tide_string = ""
        for data in tide_data:
            tide_string += data + "\n"
        #trim off last newline
        tide_string = tide_string[:-1]
        return tide_string
                 
    else:
        return "error fetching tide data"
    
def get_weather(lat=0, lon=0):
    weather = ""
    if float(lat) == 0 and float(lon) == 0:
        return "no location data: does your device have GPS?"
    weather_url = "https://forecast.weather.gov/MapClick.php?FcstType=text&lat=" + str(lat) + "&lon=" + str(lon)
    weather_data = requests.get(weather_url, timeout=URL_TIMEOUT)
    if(weather_data.ok):
        soup = bs.BeautifulSoup(weather_data.text, 'html.parser')
        table = soup.find('div', id="detailed-forecast-body")

        if table is None:
            return "no weather data found on NOAA for your location"
        else:
            #get rows
            rows = table.find_all('div', class_="row")
        
        #extract data from rows
        for row in rows:
            #shrink the text
            line = row.text.replace("Monday", "Mon ") \
                           .replace("Tuesday", "Tue ") \
                           .replace("Wednesday", "Wed ") \
                           .replace("Thursday", "Thu ") \
                           .replace("Friday", "Fri ") \
                           .replace("Saturday", "Sat ") \
                           .replace("Today", "Today ") \
                           .replace("Tonight", "Tonight ") \
                           .replace("Tomorrow", "Tomorrow ") \
                           .replace("This Afternoon", "Afternoon ") \
                           .replace("northwest", "NW") \
                           .replace("northeast", "NE") \
                           .replace("southwest", "SW") \
                           .replace("southeast", "SE") \
                           .replace("north", "N") \
                           .replace("south", "S") \
                           .replace("east", "E") \
                           .replace("west", "W") \
                           .replace("Northwest", "NW") \
                           .replace("Northeast", "NE") \
                           .replace("Southwest", "SW") \
                           .replace("Southeast", "SE") \
                           .replace("North", "N") \
                           .replace("South", "S") \
                           .replace("East", "E") \
                           .replace("West", "W") \
                           .replace("precipitation", "precip") \
                           .replace("showers", "shwrs") \
                           .replace("thunderstorms", "t-storms")
            #only grab a few days of weather
            if len(weather.split("\n")) < DAYS_OF_WEATHER:
                weather += line + "\n"
        #trim off last newline
        weather = weather[:-1]
    
        return weather

    else:
        return "error fetching weather data"
    
