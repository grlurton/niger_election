from flask import Flask
from flask import render_template
import json
from pymongo import MongoClient
from bson import json_util
from bson.json_util import dumps

app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'voter'
COLLECTION_NAME = 'project'
FIELDS = {'locality' : True, 'latitude': True, 'longitude': True, 'n_population': True, '_id':False}

@app.route("/")
def index():
	return render_template("index2.html")

@app.route("/data")
def voters_project():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_NAME]
	projects = collection.find(projection = FIELDS)

	json_projects = []
	for project in projects:
		json_projects.append(project)
	json_projects = json.dumps(json_projects, default = json_util.default)
	connection.close()
	return json_projects
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8889, debug = True)
