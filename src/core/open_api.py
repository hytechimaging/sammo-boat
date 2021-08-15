# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import json
import requests as rq


class SammoOpenApi:
    urlDB = "http://localhost:8000"
    failedConnexionMsg = "*** Connection to data base failed."

    @staticmethod
    def onClickTestButton():
        print("**** Read data base :")
        print(json.dumps(SammoOpenApi.readAll(), indent=4))
        print("**** Read one row :")
        print(SammoOpenApi.readOne("Farrell"))
        print("**** Add a row : Zitta Frédéric")
        print(SammoOpenApi.addPerson("Zitta", "Frederic"))
        print(json.dumps(SammoOpenApi.readAll(), indent=4))
        print("**** Modify a row : the first name of Zitta")
        print(SammoOpenApi.updatePerson("Zitta", "Guillaume"))
        print(json.dumps(SammoOpenApi.readAll(), indent=4))
        print("**** Delete a row : Zitta")
        print(SammoOpenApi.delPerson("Zitta"))
        print(json.dumps(SammoOpenApi.readAll(), indent=4))

    @staticmethod
    def readAll():
        try:
            result = rq.get("{}/api/people".format(SammoOpenApi.urlDB))
            outputAsDictionary = json.loads(result.text)
            return outputAsDictionary
        except rq.exceptions.RequestException:
            print(SammoOpenApi.failedConnexionMsg)

    @staticmethod
    def readOne(lname: str):
        try:
            result = rq.get(
                "{}/api/people/{}".format(SammoOpenApi.urlDB, lname)
            )
            return result.text
        except rq.exceptions.RequestException:
            print(SammoOpenApi.failedConnexionMsg)

    @staticmethod
    def addPerson(lname: str, fname: str):
        try:
            person = {"fname": fname, "lname": lname}
            rq.post("{}/api/people".format(SammoOpenApi.urlDB), json=person)
        except rq.exceptions.RequestException:
            print(SammoOpenApi.failedConnexionMsg)

    @staticmethod
    def delPerson(lname: str):
        try:
            rq.delete("{}/api/people/{}".format(SammoOpenApi.urlDB, lname))
        except rq.exceptions.RequestException:
            print(SammoOpenApi.failedConnexionMsg)

    @staticmethod
    def updatePerson(lname: str, fname: str):
        try:
            person = {"fname": fname, "lname": lname}
            rq.put(
                "{}/api/people/{}".format(SammoOpenApi.urlDB, lname),
                json=person,
            )
        except rq.exceptions.RequestException:
            print(SammoOpenApi.failedConnexionMsg)
