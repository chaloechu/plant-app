from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime 
import io
from mimetypes import guess_type, guess_extension
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

## CONSTANTS
EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.cwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

class Asset(db.Model):
    """
    Asset Model
    """
    __tablename__ = "asset"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    base_url = db.Column(db.String, nullable = False)
    salt = db.Column(db.String, nullable = False)
    extension = db.Column(db.String, nullable = False)
    width = db.Column(db.Integer, nullable = False)
    height = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.Datetime, nullable = False)

    def __init__(self, **kwargs):
        """
        Initializes an asset object
        """
        self.create(kwargs.get("image_data"))
    
    def serialize(self):
        """
        Serializes an Asset object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }


    def create(self, image_data):
        """
        Given an image in base64 encoding, does the following:
            1. Rejects the image if it is not a supported filename 
            2. Generate a random string for the image filename
            3. Decodes the iamge and attempts to upload to AWS
        """
        # if amazon breaks, our app doesn't break
        try:
            ext = guess_extension(guess_type(image_data[0]))[1:]
            # photo is not a png, jpg, gif, or jpeg
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} is not valid!")

            # produces the random string 
            salt = "".join(
                random.SystemRandom().choice (
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            # remove header from base64 string
            img_str = re.sub("^data:image./+;base64,", "", image_data)
            # decode base64
            img_data = base64.b64decode(img_str)
            # convert image data from binary into img data that Python actually understands
            img = Image.open(BytesIO(image_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datatime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"

            self.upload(img, img_filename)


        except Exception as e: 
            print(f"Error when creating image: {e}")
    
    def upload(self, img, img_filename):
        """
        Tries to upload the image into the specified S3 bucket
        """
        try:
            # save image in temporary location in our computer in order for it to be uploaded
            img_temp_loc = f"{BASE_DIR/img_filename}"
            img.save(img_temp_loc)


            # upload img into s3 bucket
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temp_loc, S3_BUCKET_NAME, img_filename)

            # make image avail to anybody
            # boto3 is a 
            s3_resource = boto3.resource("s3")
            # make sure that the image URL is publicly accessible
            object_acl = s3_resource.ObjectACL(S3_BUCKET_NAME, img_filename)
            object_acl.put(ACL = "public-read")

            # remove image from the temp location
            os.remove(img_temp_loc)

        except Exception as e:
            print(f"Error when uplading image: {e}")

tag_association_table = db.Table(
  "tag_association",
  db.Column("plant_id", db.Integer, db.ForeignKey("plants.id")),
  db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
)

class Plant(db.Model):
  """
  Class for a Plant 
  """
  __tablename__ = "plants"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False)
  scientific_name = db.Column(db.String, nullable=False)
  last_watered = db.Column(db.String, nullable=False)
  notes = db.Column(db.String, nullable=False)
  tags = db.relationship("Tag", secondary = tag_association_table, back_populates="tagged_plants")

  def __init__(self, **kwargs):
    self.name = kwargs.get("name", "Unnamed")
    self.scientific_name = kwargs.get("scientific_name", "")
    self.last_watered = kwargs.get("last_watered", "Unknown")
    self.notes = kwargs.get("notes", "")

  def serialize(self):
    return {
      "id": self.id,
      "name": self.name,
      "scientific_name": self.scientific_name,
      "last_watered": self.last_watered,
      "notes": self.notes,
      "tags": [t.serialize() for t in self.tags]
    }
  
  def simple_serialize(self):
    return {
      "id": self.id,
      "name": self.name,
      "scientific_name": self.scientific_name,
      "last_watered": self.last_watered,
      "notes": self.notes
    }

class Tag(db.Model):
  """
  Class for a Tag
  """
  __tablename__ = "tags"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False) 
  tagged_plants = db.relationship("Plant", secondary = tag_association_table, back_populates="tags")

  def __init__(self, **kwargs):
    self.name = kwargs.get("name", "untitled")

  def serialize(self):
    return {
      "name": self.name,
      "tagged_plants": [p.serialize() for p in self.tagged_plants]
    }
  
  def simple_serialze(self):
    return {
      "name": self.name
    }
