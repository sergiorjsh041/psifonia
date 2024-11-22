import argparse
import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

g=3
h=5

parser = argparse.ArgumentParser(description="Setear votante")
parser.add_argument('--id', type=str, help="id del votante")
parser.add_argument('--NT', type=int, help="cantidad de tellers")
parser.add_argument('--NTH',type=int, help="cantidad de tellers honestos")
parser.add_argument('--NC',type=int,help="cantidad de candidatos")

args = parser.parse_args()
id_votante = args.id
nt=args.NT
nth=args.NTH
nc=args.NC

# creación de los votos
papeleta=[0]*nc
posicion=random.randint(0,len(papeleta)-1)
papeleta[posicion]=1
print(f'{id_votante}: Papeleta de votante = {papeleta}')

candidatos=dict()

print(f"{id_votante}: Creando polinomios para cada candidato")
for i in range(nc):
    #polinomio 1
    coef1=[]
    for j in range(nth):
        coef1.append(random.randint(1,100))
    
    #polinomio 2
    coef2=[papeleta[i]]
    for j in range(nth-1):
        coef2.append(random.randint(1,100))
    candidatos[i]=[coef1,coef2]

commitments=dict()
print(f"{id_votante}: Polinomios creados, inicio de calculo de commitments")
for i in range(nc):
    coef1, coef2 = candidatos[i]
    commits=[]
    for j in range(len(coef1)):
        commits.append((g**coef1[j])*(h**coef2[j]))
    commitments[i]=commits

print(f"{id_votante}:  Envio de commitments a Bulletin Board")

url = "http://127.0.0.1:5000/public_commitments"
datos = {"id": id_votante, 
         'commitments':commitments, 
         'wfp': {'wfp1': None, 'wfp2': None}, 
         'sign': None}
respuesta = requests.post(url, json=datos)
print(f'{id_votante}: respuesta Bulletin Board = {respuesta.json()}')

print(f"{id_votante}: Inicio de envio de evaluaciones a tellers")

# Función para enviar datos a un teller
def enviar_a_teller(i):
    print(f"{id_votante}: Envío a teller {i}")
    teller_url = "http://localhost:" + str(5001 + i) + "/commitment"
    id_teller = i + 1
    eval = dict()
    for j in range(nc):
        coef1, coef2 = candidatos[j]
        G = 0
        H = 0
        e = 0
        for k in range(len(coef1)):
            G += coef1[k] * (id_teller) ** e
            H += coef2[k] * (id_teller) ** e
            e += 1
        eval[j] = {"G": G, "H": H}
    datos = {"i": id_votante, "Eval": eval, "Sign": None}
    respuesta = requests.post(teller_url, json=datos)
    print(f'{id_votante}: Respuesta teller {id_teller} = {respuesta.json()}')

# Enviar datos a cada teller en paralelo
with ThreadPoolExecutor(max_workers=nt) as executor:
    futures = [executor.submit(enviar_a_teller, i) for i in range(nt)]
    for future in as_completed(futures):
        future.result()  # Esperar a que cada tarea termine
print(f'{id_votante}: Proceso Finalizado')