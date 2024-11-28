import argparse
import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from ecutils.curves import *

# parser desde terminal
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
'''
creación de los votos, para soportar multiplicación de puntos en curva elipticas, ecutils no acepta directamente multiplicar por 0,
por lo que la papeleta se crea con un 1 y un 2 en una posición aleatoria
'''
papeleta=[1]*nc
posicion=random.randint(0,len(papeleta)-1)
papeleta[posicion]=2
print(f'{id_votante}: Papeleta de votante = {papeleta}')

'''
Se obtiene la información de la curva elíptica desde el Bulletin Board
'''
url = "http://127.0.0.1:5000/get-info"
response= requests.get(url)
data=response.json()
curve_json=data["curve"]
curve = EllipticCurve(
    p=curve_json["p"],
    a=curve_json["a"],
    b=curve_json["b"],
    G=Point(curve_json["G"]["x"],curve_json["G"]["y"]),
    n=curve_json["n"],
    h=curve_json["h"],
)
p=curve.p
n=curve.n
g=curve.G
h=curve.double_point(g)

'''
Creacion de polinomios para cada candidato, coeficientes deberían ser hasta n-1, porque hasta n-1 es el máximo exponente que se puede tener en la curva
'''
candidatos=dict()

print(f"{id_votante}: Creando polinomios para cada candidato")
for i in range(nc):
    #polinomio 1
    coef1=[]
    for j in range(nth):
        coef1.append(random.randint(1,n-1))
    
    #polinomio 2
    coef2=[papeleta[i]]
    for j in range(nth-1):
        coef2.append(random.randint(1,n-1))
    candidatos[i]=[coef1,coef2]


'''
Creación de commitments, dados los coeficientes de los polinomios, se crean los puntos en la curva elíptica
'''
commitments=dict()
print(f"{id_votante}: Polinomios creados, inicio de calculo de commitments")
for i in range(nc):
    coef1, coef2 = candidatos[i]
    commits=[]
    for j in range(len(coef1)):
        c =  curve.add_points(
                curve.multiply_point(coef1[j],g),
                curve.multiply_point(coef2[j],h)
                )
        commits.append(
            [c.x,c.y]  #punto en curva elíptica
            )
    commitments[i]=commits

'''
envío de commitments al bulletin board
'''
print(f"{id_votante}:  Envio de commitments a Bulletin Board")

url = "http://127.0.0.1:5000/public_commitments"
datos = {"id": id_votante, 
         'commitments':commitments, 
         'wfp': {'wfp1': None, 'wfp2': None}, 
         'sign': None}
respuesta = requests.post(url, json=datos)
print(f'{id_votante}: respuesta Bulletin Board = {respuesta.json()}')


'''
Evaluacion de polinomios y envío a tellers
'''
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