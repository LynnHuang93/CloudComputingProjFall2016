from flask import render_template
from flask import request
from flask import redirect, url_for
import json
#from math import hypot
#from pyspark import SparkContext, SparkConf
from app import app
from flask import request

#conf = SparkConf().setAppName("myapp").setMaster("local")
#sc = SparkContext(conf=conf)
#business_id_rdd = sc.textFile("yelp_academic_dataset_business.json")
#business_id = business_id_rdd.map(lambda x:json.loads(x))
@app.route('/')

@app.route('/index')
def index():
    user = { 'nickname': 'Lynn' } # fake user
    posts = []
    return render_template("index.html",
        itle = 'Home',
        user = user,
        posts = posts)

@app.route('/tags', methods=['GET','POST'])
def tags():
#	centerx=request.longitude
#	centery=request.latitude
#
#	wanted_id_locations = business_id.filter(lambda x:hypot(x['latitude']-centerx, x['longitude']-centery)<0.00048561816275650364)
#	res = wanted_id_locations.collect()
#	b = []
#	for a in res:
#		tags = getTags(a['business_id'])
#	    c = json.dumps({"business_id":a["business_id"], "full_address":a["full_address"], "name":a["name"], "longitude":a["longitude"], "latitude":a["latitude"], "stars":a["stars"], "tags":tags})
#	    b.append(c)
    if request.method == 'POST':
        data = request.data
        #dataDict = json.loads(data)
        print data
        #print dataDict
        return redirect(url_for('tagresult'))
    if request.method == 'GET':
        user = { 'nickname': 'Lynn' } # fake user
        b = [{"name":"tag1", "score":1},{"name":"tag2", "score":1}]
        #map.put(request.location, b) #[{"name": "Mariscos Vuelve a La Vida", "business_id": "oa8lhYj-mTKlL_amkJSu2Q", "longitude": -112.1513005, "full_address": "2915 N 43rd Ave\\nPhoenix, AZ 85031", "stars": 2.5, "latitude": 33.4813351}, {"name": "Ta\'Carbon", "business_id": "I4uDkxbTLt5l1JFkcG1e7g", "longitude": -112.151272, "full_address": "2929 N 43rd Ave\\nPhoenix, AZ 85019", "stars": 4.5, "latitude": 33.48189}]
        return render_template("tags.html",title='Tags',user=user,posts=b)
'''
def tagresult():
    data = request.data
    dataDict = json.loads(data)
    print data
    print dataDict
'''
@app.route('/tagresult', methods=['GET'])
def tagresult():
    print "ok"
    b = [{"name":"tag1", "score":1},{"name":"tag2", "score":1}]
    return render_template("tagresult.html",title='TagResult',posts=b)
