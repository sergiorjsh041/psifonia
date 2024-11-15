import requests

url = "http://127.0.0.1:5000/get-info"
datos = {"id": 5,"G": None,"q": None, "g": 3, "h": 5, "votantes": {1: {"pk": 5, "IP": "", "Puerto": 5000}}}
respuesta = requests.get(url)

print(respuesta.json())

url = "http://127.0.0.1:5000/get-bulletin-board"
datos = {"id": 5, "g": 3, "h": 5, "votantes": {1: {"pk": 5, "IP": "", "Puerto": 5000}}}
respuesta = requests.get(url)

print(respuesta.json())