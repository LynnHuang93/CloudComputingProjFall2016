#!/usr/bin/python3
"""Simple server to demonstrate how to use Google+ Sign-In."""
from flask import Flask, jsonify
from flask import render_template
from flask import request
from elasticsearch import Elasticsearch
import json
import flask_googlemaps
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from flask import Flask
from flask import render_template
from pyes import *
from flask import request
import json
import requests
from wsgiref.simple_server import make_server
import flask_googlemaps
import operator
#from fs_api import FSAPI
import foursquare_venue
import google_places

from watson_developer_cloud import AlchemyLanguageV1
from pyes import *

alchemy_language = AlchemyLanguageV1(api_key='2228ee4b738811d86e6a952186c24cadfc885437')
REGION = 'us-east-1'
global conn
conn = ES('http://search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com')

#yelp:
# ['{"name": "Mariscos Vuelve a La Vida", "business_id": "oa8lhYj-mTKlL_amkJSu2Q",
# "longitude": -112.1513005, "full_address": "2915 N 43rd Ave\\nPhoenix, AZ 85031", "stars": 2.5, "latitude": 33.4813351}',
# '{"name": "Ta\'Carbon", "business_id": "I4uDkxbTLt5l1JFkcG1e7g",
# "longitude": -112.151272, "full_address": "2929 N 43rd Ave\\nPhoenix, AZ 85019", "stars": 4.5, "latitude": 33.48189}']
#4square:
global fs_rank
global yelp_info
global venue_list

APPLICATION_NAME = 'FoodeeTrendzapp'

location_dictionary = dict()
latitude_dict = dict()
longitude_dict = dict()
business_name_dict = dict()

application = Flask(__name__)
application.config['GOOGLEMAPS_KEY'] = "AIzaSyC0HM8yvrxNK1EcNfxeczoDA5HwGORYAc0"

flask_googlemaps.GoogleMaps(application)

auth = Oauth1Authenticator(
    consumer_key='2fNxjuriouw4CC5PLKccGA',
    consumer_secret='hQKfMMBaVihqLQg6po3ipbT4Rn0',
    token='6y_3oDuZECvAGOf25BEWSvsnXFX8T1J3',
    token_secret='2H8SwkL4g7N6mTEnV-KAr6XRdyc'
)

yelp_client = Client(auth)
es = Elasticsearch([{'host':'search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com','port':80,'use_ssl':False}])


def foodtrendz(lat, long):
    global venue_list
    venue_list = foursquare_venue.rated_list_checkin(lat, long, 50)
    fs_dict = {}
    if venue_list:
        for venue in venue_list:
            fs_dict[venue.name] = venue.rank
    return fs_dict


@application.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@application.route('/selectedlocation', methods=['POST','GET'])
def selectedlocation():
    #if request.method == 'GET':
    latitude = request.form['latitude']
    longitude =request.form['longitude']
    latitude_dict[request.remote_addr] = latitude
    longitude_dict[request.remote_addr] = longitude

    conn = ES('http://search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com')
    conn.indices.delete_index("test1-index")
    conn.indices.create_index('test1-index')
    places_list = google_places.search(latitude,longitude,50)
    global result
    result=[]

    count=1
    for place in places_list:
        count=count+1
        print(len(place.reviews))
        for i in range(len(place.reviews)):
            result.append({'name':place.name,'review':place.reviews[i]['text']})
        final = json.dumps(result)
        print (final,'\n')
        if count==len(places_list):
            conn.index({'placelist':final},'test1-index',"test1-type")

    response = yelp_client.search_by_coordinates(latitude, longitude, radius_filter=50)
    business_with_tags=[]
    for business in response.businesses:
        query_body = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "match": {"business_id": business.id}
                    }
                }
            }
        }
        es_res = es.search(index='yelp', body=query_body)
        tags = []
        for hit in es_res['hits']['hits']:
            tags.append(hit['_source'])
        business_info_dict = dict()
        business_info_dict['name'] = business.name
        business_info_dict['id'] = business.id
        business_info_dict['stars'] = business.rating
        business_info_dict['latitude'] = business.location.coordinate.latitude
        business_info_dict['longitude'] = business.location.coordinate.longitude
        business_info_dict['tags'] = tags
        business_with_tags.append(business_info_dict)
    location_dictionary[request.remote_addr] = business_with_tags
    return json.dumps(location_dictionary)#render_template('tags.html',posts=b)

@application.route('/tags', methods=['POST','GET'])
def tags():
    if request.method == 'GET':
        b = location_dictionary[request.remote_addr]
        s = set()
        for business in b:
            for tag in business['tags']:
                s.add(tag['tag'])
        #del location_dictionary[request.remote_addr]
        #return render_template("tags.html",posts=b)
        return render_template('tags.html', posts=list(s))
    if request.method == 'POST':
        tags = request.form['tags']
        b = location_dictionary[request.remote_addr]
        new_list = []
        for business_dict in b:
            flag = False
            for t in business_dict['tags']:
                if t['tag'] in tags:
                    flag = True
                    break
            if flag :
                new_list.append(business_dict)
        location_dictionary[request.remote_addr] = new_list
        return 'ok'

@application.route('/search', methods=['GET','POST'])

def generate_ranking():
    global yelp_info
    yelp_info = location_dictionary[request.remote_addr]
    latitude = latitude_dict[request.remote_addr]
    longitude = longitude_dict[request.remote_addr]
    global fs_rank
    #fs_rank = foodtrendz(33.48189,-112.151272)
    fs_rank = foodtrendz(latitude,longitude)
    rank_list = {} # name: new_rank
    geo_list = []
    yelp_dict = {}
    yelp_geodict={}
    for item in yelp_info:
        yelp_dict[item['name']] = item['stars']
        yelp_geodict[item['name']]=[item['latitude'],item['longitude']]
    fs_len = len(fs_rank.keys())
    if fs_len == 0:
        rank_list=yelp_dict
        for i in yelp_geodict:
            geo_list.append(str(yelp_geodict[i][0]) + ',' + str(yelp_geodict[i][1]))

    for i in fs_rank :
        f = fs_rank[i]
        if i in yelp_dict:
            y = yelp_dict[i]
            weight_f = 0.4
            weight_y = 0.6
            rank = ((fs_len-f+1) / fs_len) * weight_f + (y / 5)* weight_y
            rank_list[i] = rank
            geo_list.append(str(yelp_geodict[i][0]) + ',' + str(yelp_geodict[i][1]))
    res = sorted(rank_list.items(), key=operator.itemgetter(1))
    return render_template('restaurantlist.html', rank_list=res, coord_list = geo_list)


@application.route('/detail', methods=['POST'])
def generate_detail():
    restaraunt_name=request.form['restaurants']
    rn = restaraunt_name.split(',')
    name = rn[0]
    full_info_list=[]
    geo=[]
    for item in yelp_info:
        geo=[]
        if name in item['name']:
            name = item['name']
            full_info_list.append(item)
            geo.append(str(item['latitude']) + ',' + str(item['longitude']))
    res = 0
    for venue in venue_list:
        if venue.name == name:
            res = venue.checkin_count

    query_body = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": {
                        "match": {"name": name}
                    }
                }
            }
        }
    es_res = es.search(index='kafka-id', body=query_body)
    cus_res = es.search(index='review-id', body=query_body)
    googlereviews = []
    for hit in es_res['hits']['hits']:
        googlereviews.append(hit['_source'])
    customerreviews = []
    for hit in cus_res['hits']['hits']:
        customerreviews.append(hit['_source'])
    return render_template('detail.html', tag_list=full_info_list, coord_list = geo, checkin=res, googlereviews=googlereviews, customerreviews= customerreviews)

@application.route('/reviewnav',methods=['POST'])
def reviewnav():
    business_name = request.form['business_name']
    business_name_dict[request.remote_addr]=business_name
    return render_template('review.html', business_name=business_name)

@application.route('/review',methods=['POST','GET'])
def review():
    tempary = request.form['review'] #'b/..'
    temp=[]
    business_name = business_name_dict[request.remote_addr]
    outer=[]
    result=alchemy_language.keywords(text=tempary,sentiment=True,emotion=True)
    for j in range(len(result['keywords'])):
        if float(result['keywords'][j]['relevance'])>0.45:
            temp.append({'sentiment':result['keywords'][j]['sentiment'], 'tag':result['keywords'][j]['text']})
    outer.append({'name':business_name,'contain':temp})
    for i in range(len(outer)):
        contain=outer[i]['contain']
        for j in range(len(contain)):
            sentiment_type=contain[j]['sentiment']['type']
            if sentiment_type=='neutral':
                score='0'
            else:
                score=contain[j]['sentiment']['score']
            tag=contain[j]['tag']
            conn.index({'tag':tag,'sentiment':{'type':sentiment_type,'score':score},'name': business_name},'review-id',"test-type")

    return render_template('index.html',status='success')

@application.route('/reviewsubmit',methods=['POST','GET'])
def reviewsubmit():
    return render_template('review.html',status='success')

if __name__ == '__main__':
  application.debug = True
  application.run()
