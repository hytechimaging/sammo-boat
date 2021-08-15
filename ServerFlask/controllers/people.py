from datetime import datetime
from flask import make_response, abort
import json


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


def ReadDatasFromFile():
   with open("datas.json") as json_file:
        PEOPLE = json.load(json_file)
        return PEOPLE

def WriteDatasToFile(dict):
   with open("datas.json", 'w') as json_file:
        json.dump(dict, json_file, indent=4)


# Create a handler for our read (GET) people
def read_all():
    PEOPLE = ReadDatasFromFile()
    return PEOPLE #[PEOPLE[key] for key in sorted(PEOPLE.keys())]


def read_one(lname):
    """
    This function responds to a request for /api/people/{lname}
    with one matching person from people
    :param lname:   last name of person to find
    :return:        person matching last name
    """
    PEOPLE = ReadDatasFromFile()
    print(PEOPLE)
    print('lname=' + lname)
    # Does the person exist in people?
    for person in PEOPLE:
        if person == lname:
            return PEOPLE[lname]
    # otherwise, nope, not found

    abort(404, "Person with last name {lname} not found".format(lname=lname))

    return person


def create(person):
    """
    This function creates a new person in the people structure
    based on the passed in person data
    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """
    PEOPLE = ReadDatasFromFile()
    print(PEOPLE)
    lname = person.get("lname", None)
    fname = person.get("fname", None)
    print("Reçu = " + lname + " " + fname)

    # Does the person exist already?
    if lname not in PEOPLE and lname is not None:
        PEOPLE[lname] = {
            "lname": lname,
            "fname": fname,
            "timestamp": get_timestamp(),
            }
        WriteDatasToFile(PEOPLE)
        return make_response(
            "{lname} successfully created".format(lname=lname), 201
        )

    # Otherwise, they exist, that's an error
    else:
        abort(406, "Person with last name {lname} already exists".format(lname=lname))


def update(lname, person):
    """
    This function updates an existing person in the people structure
    :param lname:   last name of person to update in the people structure
    :param person:  person to update
    :return:        updated person structure
    """
    PEOPLE = ReadDatasFromFile()
    # Does the person exist in people?
    if lname in PEOPLE:
        PEOPLE[lname]["fname"] = person.get("fname")
        PEOPLE[lname]["timestamp"] = get_timestamp()
        WriteDatasToFile(PEOPLE)
        return PEOPLE[lname]

    # otherwise, nope, that's an error
    else:
        abort(404, "Person with last name {lname} not found".format(lname=lname))


def delete(lname):
    """
    This function deletes a person from the people structure
    :param lname:   last name of person to delete
    :return:        200 on successful delete, 404 if not found
    """
    PEOPLE = ReadDatasFromFile()
    # Does the person to delete exist?
    if lname in PEOPLE:
        del PEOPLE[lname]
        WriteDatasToFile(PEOPLE)
        return make_response("{lname} successfully deleted".format(lname=lname), 200)

    # Otherwise, nope, person to delete not found
    else:
        abort(404, "Person with last name {lname} not found".format(lname=lname))
