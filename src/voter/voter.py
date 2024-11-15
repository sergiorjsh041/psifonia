import argparse
import requests
import random

g=3
h=5

#2 CANDIDATOS

parser = argparse.ArgumentParser(description="Setear votante")
parser.add_argument('--id', type=str, help="id del votante")
parser.add_argument('--votoA', type=int, help="voto del votante")
parser.add_argument('--votoB', type=int, help="voto del votante")

args = parser.parse_args()
id_votante = args.id


votoA= args.votoA
votoB= args.votoB
a_1A = random.randint(1, 100)
a_2A = random.randint(1, 100)
a_3A = random.randint(1, 100)
b_1A=int(votoA)
b_2A = random.randint(1, 100)
b_3A = random.randint(1, 100)

a_1B = random.randint(1, 100)
a_2B = random.randint(1, 100)
a_3B = random.randint(1, 100)
b_1B=int(votoB)
b_2B = random.randint(1, 100)
b_3B = random.randint(1, 100)

BA= (g**a_1A)*(h**b_1A)
BA1= (g**a_2A)*(h**b_2A)
BA2= (g**a_3A)*(h**b_3A)

BB= (g**a_1B)*(h**b_1B)
BB1= (g**a_2B)*(h**b_2B)
BB2= (g**a_3B)*(h**b_3B)

url = "http://127.0.0.1:5000/public_commitments"
datos = {"id": id_votante, 
         'commitments':{'A': {'B': BA, 'B1': BA1, 'B2': BA2}, 'B': {'B': BB, 'B1': BB1, 'B2': BB2}}, 
         'wfp': {'wfp1': None, 'wfp2': None}, 
         'sign': None}
respuesta = requests.post(url, json=datos)


teller_url = "http://localhost:5001/commitment"
id_teller=1

GA= a_1A + a_2A*id_teller + a_3A*(id_teller**2)
HA= b_1A + b_2A*id_teller + b_3A*(id_teller**2) 

GB= a_1B + a_2B*id_teller + a_3B*(id_teller**2)
HB= b_1B + b_2B*id_teller + b_3B*(id_teller**2)

datos= {"i": id_votante, "Eval": {'A': {'G': GA, 'H': HA}, 'B': {'G': GB, 'H': HB}}, "Sign": None}
respuesta = requests.post(teller_url, json=datos)
print(respuesta.json())

teller_url = "http://localhost:5002/commitment"
id_teller=2

GA= a_1A + a_2A*id_teller + a_3A*(id_teller**2)
HA= b_1A + b_2A*id_teller + b_3A*(id_teller**2) 

GB= a_1B + a_2B*id_teller + a_3B*(id_teller**2)
HB= b_1B + b_2B*id_teller + b_3B*(id_teller**2)

datos= {"i": id_votante, "Eval": {'A': {'G': GA, 'H': HA}, 'B': {'G': GB, 'H': HB}}, "Sign": None}
respuesta = requests.post(teller_url, json=datos)
print(respuesta.json())

teller_url = "http://localhost:5003/commitment"
id_teller=3

GA= a_1A + a_2A*id_teller + a_3A*(id_teller**2)
HA= b_1A + b_2A*id_teller + b_3A*(id_teller**2) 

GB= a_1B + a_2B*id_teller + a_3B*(id_teller**2)
HB= b_1B + b_2B*id_teller + b_3B*(id_teller**2)

datos= {"i": id_votante, "Eval": {'A': {'G': GA, 'H': HA}, 'B': {'G': GB, 'H': HB}}, "Sign": None}
respuesta = requests.post(teller_url, json=datos)
print(respuesta.json())

teller_url = "http://localhost:5004/commitment"
id_teller=4

GA= a_1A + a_2A*id_teller + a_3A*(id_teller**2)
HA= b_1A + b_2A*id_teller + b_3A*(id_teller**2) 

GB= a_1B + a_2B*id_teller + a_3B*(id_teller**2)
HB= b_1B + b_2B*id_teller + b_3B*(id_teller**2)

datos= {"i": id_votante, "Eval": {'A': {'G': GA, 'H': HA}, 'B': {'G': GB, 'H': HB}}, "Sign": None}
respuesta = requests.post(teller_url, json=datos)
print(respuesta.json())