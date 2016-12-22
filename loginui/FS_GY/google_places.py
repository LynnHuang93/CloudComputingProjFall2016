import json
from urllib.request import urlopen

class google_buss:
    def __init__(self, name, address,rating,reviews):
        self.name = name
        self.address = address
        self.rating = rating
        self.reviews = reviews

google_search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&types=food&key={}'
google_place_url = 'https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}'
google_api_key='AIzaSyCw7p6HofmStntau71mNprwf9YzdTU6hio'

def make_request(venuesearch_url):
    return json.loads(urlopen(venuesearch_url).read().decode(encoding='UTF-8'))


def search(lat, lng, distance):
    gs_url = google_search_url.format(lat, lng, distance, google_api_key)
    place_list = []

    try:
        data = make_request(gs_url)

        for result in data['results']:
            if 'restaurant' in result['types']:
                place = search_place(result['place_id'])
                place_list.append(place)

    except Exception as e:
        print(e)

    return place_list


def search_place(place_id):

    url = google_place_url.format(place_id, google_api_key)

    try:
        data = make_request(url)

        place = data['result']
        return google_buss(place['name'],
                        place['formatted_address'],
                        place['rating'],
                        place['reviews'],
                        )
    except Exception as e:
        print(e)
