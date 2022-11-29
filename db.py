from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
