# plant-app - fa22 team 11 backend

## implemented routes:
1. GET all plants &rarr; returns a list of all the plants in the database
2. Create (POST) a new plant &rarr; user inputs information to initialize and create a new plant in the database
3. GET a plant by id &rarr; returns one plant with the associated id (if it exists)
4. DELETE a plant by id &arr; allows the user to delete the plant associated with the input id (if it exists)
5. Update (POST) plant field(s) &rarr; user inputs the values for the field(s) they want to change in an existing plant
6. GET all tags &rarr; returns a list of all the tags that have been created 
7. Create (POST) a new tag &rarr; user inputs the name of the tag that they want to create 
8. Add (POST) tag to a plant &rarr; user inputs the id of the tag (if it exists) that they want to attach to a specific plant (if it exists)
9. Update (POST) to just watered &rarr; sets the last_watered attribute of a plant to the current time

## database models:
1. plant
  - name: string
  - scientific_name: string
  - last_watered: string (in milliseconds)
  - notes: string
  - tags: list of tags attached to this plant
2. tag
  - name: string
  - tagged_plants: list of plants with this tag
  
## database model relationships
plant &larr;&rarr; tag - many to many

### by chloe chu & tiffany pan



