import json, os
from datetime import datetime
from db import db, Plant, Tag
from flask import Flask, request
from db import Asset

app = Flask(__name__)
db_filename = " "

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# default responses

def success_response(data, code=200):
  """
  Returns a success response for a route
  """
  return json.dumps(data), code

def failure_response(message, code=404):
  """
  Returns a failure response fro a route
  """
  return json.dumps({"error": message}), code


# app routes

@app.route("/")
def test_endpoint():
  return success_response(os.environ["GROUP"] + " hack challenge endpoint :)")

@app.route("/api/plants/")
def get_plants():
  """
  Endpoint for getting all plants
  """
  plants = [plant.serialize() for plant in Plant.query.all()]
  return success_response({"plants": plants})

@app.route("/api/plants/", methods=["POST"])
def create_plant():
  """
  Endpoint for creating a new plant
  """
  body = json.loads(request.data)
  if body.get("name") is None or body.get("scientific_name") is None:
    return failure_response("Bad Request", 400)

  watered = body.get("last_watered")
  if watered is None:
    watered = "Unknown"
  notes = body.get("notes")
  if notes is None:
    notes = ""
  new_plant = Plant(name = body.get("name"), scientific_name = body.get("scientific_name"), last_watered = watered, notes = notes)
  db.session.add(new_plant)
  db.session.commit()
  return success_response(new_plant.serialize(), 201)

@app.route("/api/plants/<int:plant_id>/")
def get_plant_by_id(plant_id):
  """
  Endpoint for getting a plant by their id
  """
  plant = Plant.query.filter_by(id=plant_id).first()
  if plant is None:
    return failure_response("Plant not found!")
  return success_response(plant.serialize())

@app.route("/api/plants/<int:plant_id>/", methods=["DELETE"])
def delete_plant_by_id(plant_id):
  """
  Endpoint for deleting a plant by their id
  """
  plant = Plant.query.filter_by(id=plant_id).first()
  if plant is None:
    return failure_response("Plant not found!")
  db.session.delete(plant)
  db.session.commit()
  return success_response(plant.serialize())

@app.route("/api/plants/<int:plant_id>/", methods=["POST"])
def update_plant_by_id(plant_id):
  """
  Endpoint for updating a plant field
  """
  plant = Plant.query.filter_by(id=plant_id).first()
  if plant is None:
    return failure_response("Plant not found!")
  body = json.loads(request.data)
  name = body.get("name")
  scientific_name = body.get("scientific_name")
  last_watered = body.get("last_watered")
  notes = body.get("notes")
  if name is not None:
    plant.name = name
  if scientific_name is not None:
    plant.scientific_name = scientific_name
  if last_watered is not None:
    plant.last_watered = last_watered
  if notes is not None:
    plant.notes = notes
  
  db.session.commit()
  return success_response(plant.simple_serialize(), 201)
  

@app.route("/api/tags/")
def get_tags():
  """
  Endpoint for getting all tags
  """
  tags = [tag.serialize() for tag in Tag.query.all()]
  return success_response({"tags": tags})

@app.route("/api/tags/", methods=["POST"])
def create_tag():
  """
  Endpoint for creating a tag
  """
  body = json.loads(request.data)
  if body.get("name") is None:
    return failure_response("Bad Request", 400)
  
  tag = Tag(name = body.get("name"))
  db.session.add(tag)
  db.session.commit()
  return success_response(tag.serialize(), 201)

@app.route("/api/plants/<int:plant_id>/add/", methods=["POST"])
def add_tag_to_plant(plant_id):
  """
  Endpoint to add a tag to a plant
  """
  plant = Plant.query.filter_by(id=plant_id).first()
  if plant is None:
    return failure_response("Plant not found!")
  body = json.loads(request.data)
  tag_id = body.get("tag_id")
  if tag_id is None:
    return failure_response("Bad Request", 400)
  tag = Tag.query.filter_by(id=tag_id).first()
  if tag is None:
    return failure_response("Tag not found!")
  
  plant.tags.append(tag)
  tag.tagged_plants.append(plant)
  db.session.commit()
  return success_response(plant.serialize())

@app.route("/api/plants/<int:plant_id>/", methods=["POST"])
def update_watered(plant_id):
  """
  Endpoint for updating a plant's last watered field
  """
  plant = Plant.query.filter_by(id=plant_id).first()
  if plant is None:
    return failure_response("Plant not found!")

  # will prolly need to convert this to a readable String actually
  plant.last_watered = datetime.datetime.now()

  db.session.commit()
  return success_response(plant.serialize())

@app.route("/upload/", methods=["POST"])
def upload():
    """
    Endpoint for uploading an image to AWS given its base64 form,
    then storing/returning the URL of that image
    """
    body = json.loads(request.data)
    image_data = body.get("image_data")

    if image_data is None:
        return failure_response("No base64 image found!")

    asset = Asset(image_data = image_data)
    db.session.add(asset)
    db.session.commit()

    return success_response(asset.serialize(), 201)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000, debug=True)

