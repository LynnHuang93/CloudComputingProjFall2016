import time
import json
from urllib.request import urlopen

#clientId='NCCWW3BJFASFFMU0JSFZVYGXZMI5TUGVRGX0POKDW11HOWXU'
#client_secret='4PVBXZXWMECT1E5JF5CRQP3EHEGHU2HLUB3MUJWZFB4YVKL0'

clientId= 'YKBJMILK4OFZUI34J3ORRE4NHKD55TSDLQOQNKPATRWHFVT5'
client_secret = '2SSWLCMKMSVJW2NRD1YPNI1HTXX24OARYE03K51RMY2VDSN2'
category_id='4d4b7105d754a06374d81259' #Food

class fs_buss:
    def __init__(self, name, address,checkin_count,herenow):
        self.name = name
        self.address = address
        self.checkin_count = checkin_count
        self.herenow= herenow
        self.rank = 0

def make_request(venuesearch_url):
    """
    Makes a new HTTP request to the given URL
    :param url: The URL to request
    :returns: JSON response
    """

    return json.loads(urlopen(venuesearch_url).read().decode(encoding='UTF-8'))

SEARCH_URL = 'https://api.foursquare.com/v2/venues/search?ll={},{}&intent=browse&radius={}&limit=50&categoryId={}&client_id={}&client_secret={}&v={}'
def fs_venue_search(lat, lng, distance):

    fs_vs_url = SEARCH_URL.format(lat, lng, distance,category_id, clientId, client_secret,time.strftime("%Y%m%d"))
    venue_list = []

    try:
        data = make_request(fs_vs_url)
        print(data)

        for item in data['response']['venues']:
            venue = item
            if hasattr(venue, 'herenow'):
                venue_list.append(fs_buss(venue['name'],venue['location']['formattedAddress'],venue['stats']['checkinsCount'],venue['herenow']['count']))
            else:
                venue_list.append(fs_buss(venue['name'], venue['location']['formattedAddress'], venue['stats']['checkinsCount'],'NA'))
    except Exception as e:
        print(e)

    return venue_list

def rated_list_checkin(lat,lng,distance):
    venue_list=fs_venue_search(lat,lng,distance)
    #venue_list_sorted =sorted(venue_list, key=lambda fs_buss: fs_buss.checkin_count)
    venue_list = sorted(venue_list,key=lambda fs_buss: fs_buss.checkin_count, reverse=True)
    if venue_list:
        venue_list[0].rank = 1
        dupcount = 0
        prev = venue_list[0]
        for venue in venue_list[1:]:
            if venue.checkin_count == prev.checkin_count:
                venue.rank = prev.rank
                dupcount += 1
            else:
                venue.rank = prev.rank + dupcount + 1
                dupcount = 0
                prev = venue

    return venue_list

