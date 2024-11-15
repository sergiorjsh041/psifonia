import requests

url = "http://127.0.0.1:5001/get-info"
respuesta = requests.get(url)
print(respuesta.json())

url = "http://127.0.0.1:5002/get-info"
respuesta = requests.post(url)
print(respuesta.json())