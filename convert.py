from elasticsearch import Elasticsearch
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import json

auth = Oauth1Authenticator(
    consumer_key='2fNxjuriouw4CC5PLKccGA',
    consumer_secret='hQKfMMBaVihqLQg6po3ipbT4Rn0',
    token='6y_3oDuZECvAGOf25BEWSvsnXFX8T1J3',
    token_secret='2H8SwkL4g7N6mTEnV-KAr6XRdyc'
)

yelp_client = Client(auth)
es = Elasticsearch([{'host':'search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com','port':80,'use_ssl':False}])
request_body = {"settings" : {"number_of_shards": 1,"number_of_replicas": 0}}
#es.indices.create(index = 'yelp', body = request_body, ignore=400)


business_id_rdd = sc.textFile("yelp_academic_dataset_business.json")
business_id = business_id_rdd.map(lambda x:json.loads(x))
wanted_id = business_id.filter(lambda x: x['city']=="Urbana" and x['state']=="IL" and "Restaurants" in x["categories"])
res = wanted_id.collect()

for line in res:
	business_id = line['business_id']
	business_name = line['name']
	latitude = line['latitude']
	longitude = line['longitude']
	query_body = {
        "query":{
            "bool":{
                "must": {
                    "match" : { "business_id" : business_id }
                }
            }
        }
    }
	response = yelp_client.search_by_coordinates(latitude, longitude, radius_filter=50)
	yelp_api_business_id = ""
	for business in response.businesses:
		if business.name == business_name:
			yelp_api_business_id = business.id
			break
	if yelp_api_business_id != "":
		es_res = es.search(index='test-id',body=query_body)
		for hit in es_res['hits']['hits']:
			tag = hit['_source']
			tag['business_id'] = yelp_api_business_id
			#print tag
			es.index(index='yelp', doc_type='review_tag', body=tag)
	#res = es.index(tag,'yelp', 'review_tag')

'''
response = es.search(
    index='test-id',
    body={
        "query":{
            "bool":{
                "must": {
                    "match" : { "business_id" : business_id }
                  }
            }
        }
    }
)
'''