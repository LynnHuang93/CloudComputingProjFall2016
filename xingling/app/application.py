"""Simple server to demonstrate how to use Google+ Sign-In."""
from flask import Flask, jsonify
from flask import render_template
from flask import request
from elasticsearch import Elasticsearch
import json
import flask_googlemaps
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

APPLICATION_NAME = 'FoodeeTrendzapp'

location_dictionary = dict()

app = Flask(__name__)
app.config['GOOGLEMAPS_KEY'] = "AIzaSyC0HM8yvrxNK1EcNfxeczoDA5HwGORYAc0"

flask_googlemaps.GoogleMaps(app)
auth = Oauth1Authenticator(
    consumer_key='2fNxjuriouw4CC5PLKccGA',
    consumer_secret='hQKfMMBaVihqLQg6po3ipbT4Rn0',
    token='6y_3oDuZECvAGOf25BEWSvsnXFX8T1J3',
    token_secret='2H8SwkL4g7N6mTEnV-KAr6XRdyc'
)

yelp_client = Client(auth)
es = Elasticsearch([{'host':'search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com','port':80,'use_ssl':False}])


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/selectedlocation', methods=['POST','GET'])
def selectedlocation():
    #if request.method == 'GET':
    latitude = request.form['latitude']
    longitude =request.form['longitude']
    print(latitude, longitude)
    response = yelp_client.search_by_coordinates(latitude, longitude, radius_filter=50)
    business_with_tags=[]
    print("len:",len(response.businesses))
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
        print(es_res)
        tags = []
        for hit in es_res['hits']['hits']:
            print("hit:",hit)
            tags.append(hit['_source'])
        business_info_dict = dict()
        business_info_dict['name'] = business.name
        business_info_dict['id'] = business.id
        business_info_dict['stars'] = business.rating
        business_info_dict['latitude'] = business.location.coordinate.latitude
        business_info_dict['longitude'] = business.location.coordinate.longitude
        business_info_dict['tags'] = tags
        business_with_tags.append(business_info_dict)
        print("business_info_dict",business_info_dict)
    location_dictionary[request.remote_addr] = business_with_tags
    #print(latitude,longitude)
    return json.dumps(location_dictionary)#render_template('tags.html',posts=b)

@app.route('/tags', methods=['POST','GET'])
def tags():
    if request.method == 'GET':
        #latitude = request.form['latitude']
        #longitude = request.form['longitude']
        #print(latitude, longitude)
        b = location_dictionary[request.remote_addr]
        print(b)
        s = set()
        for business in b:
            for tag in business['tags']:
                s.add(tag['tag'])
        print("set:",list(s))
        #del location_dictionary[request.remote_addr]
        #return render_template("tags.html",posts=b)
        return render_template('tags.html', posts=list(s))
    else:
        tags = request.form
        print(tags)
        return 'ok'

#@app.route('/search', methods=['POST','GET'])


if __name__ == '__main__':
  app.debug = True
  app.run()