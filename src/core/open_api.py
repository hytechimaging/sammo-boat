# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

import json
import requests as rq


class SammoOpenApi:
    url = "http://localhost:8000/api"

    @staticmethod
    def onClickTestButton():
        print("**** Base de donnée distante :")
        print(json.dumps(SammoOpenApi.readAll(), indent=4))
        print("**** Lecture d'un seul enregistrement :")
        print(SammoOpenApi.readOne("Farrell"))
        print("**** Ajout d'un enregistrement : Zitta Frédéric")
        print(SammoOpenApi.addPerson("Zitta", "Frederic"))
        print(json.dumps(SammoOpenApi.readAll(), indent=4))
        print("**** Modification d'un enregistrement : le prénom de Zitta")
        print(SammoOpenApi.updatePerson("Zitta", "Guillaume"))
        print(json.dumps(SammoOpenApi.readAll(), indent=4))
        print("**** Suppression d'un enregistrement : Zitta")
        print(SammoOpenApi.delPerson("Zitta"))
        print(json.dumps(SammoOpenApi.readAll(), indent=4))

    @staticmethod
    def readAll():
        outputAsDictionary = json.loads(rq.get("http://localhost:8000/api/people").text)
        return outputAsDictionary

    @staticmethod
    def readOne(lname: str):
        return rq.get("http://localhost:8000/api/people/"+lname).text

    @staticmethod
    def addPerson(lname: str, fname: str):
        person = {"fname":fname,"lname":lname}
        rq.post("http://localhost:8000/api/people", json=person)

    @staticmethod
    def delPerson(lname: str):
        rq.delete("http://localhost:8000/api/people/" + lname)

    @staticmethod
    def updatePerson(lname: str, fname: str):
        person = {"fname":fname,"lname":lname}
        rq.put("http://localhost:8000/api/people/" + lname, json=person)
