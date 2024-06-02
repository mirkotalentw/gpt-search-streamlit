import requests


def get_city_country(url, city, country, lang='de'):
    city_normalized, country_normalized = "", ""
    
    try:
        
        if city:
            url_request = f"{url}/api?q={city}&lang={lang}&limit=3&bbox=-27.627108,33.036997,65.029825,70.750216" 
        else:
            url_request = f"{url}/api?q={country}&lang={lang}#&limit=3&bbox=-27.627108,33.036997,65.029825,70.750216"
        
        response = requests.get(url_request)
        data = response.json()
        
        found_city = False

        for feature in data['features']:
            data_properties = feature['properties']
    
            if data_properties['type'] == 'city' and not found_city:
                city_normalized = data_properties['name']
                country_normalized = data_properties['country'] 
                found_city = True  
                break  
    
            elif data_properties['type'] == 'country' and not found_city:
                country_normalized 
                break  

    except Exception as e:
        print(f"Error fetching data for city: {city}, country: {country}: {e}")

    return city_normalized, country_normalized