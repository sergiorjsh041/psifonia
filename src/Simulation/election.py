import argparse
import subprocess
import time
import random
import requests
import psutil
from ecutils.curves import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from fractions import Fraction


parser = argparse.ArgumentParser(description="Setear eleccion")
parser.add_argument('--Q', type=str, help="Pregunta de la eleccion")
parser.add_argument('--NN', type=str, nargs='+', help="Nombres de los candidatos")
parser.add_argument('--NT', type=int, help="Numero de tellers")
parser.add_argument('--NTH', type=int, help="Numero de tellers honestos")
parser.add_argument('--NV', type=int, help="Numero de votantes")

args = parser.parse_args()
Q=args.Q
NN=args.NN
NC=len(NN)
NT=args.NT
NTH=args.NTH
NV=args.NV

print(f"INICIO DE VOTACION '{Q}'")

# Crear curva elíptica
curve = secp256k1
p=curve.p
gx, gy = curve.G.x, curve.G.y
h=curve.double_point(curve.G)
hx, hy = h.x, h.y
curve_data = {
    "p": curve.p,
    "a": curve.a,
    "b": curve.b,
    "G": {"x": curve.G.x, "y": curve.G.y},
    "n": curve.n,
    "h": curve.h,
}
curve_json=curve_data

# Crear procesos para Bulletin Board y Tellers, envío de curvas
print("Creacion de Bulletin Board")
bulletin_board_process = subprocess.Popen(['start', 'cmd', '/k', 'python', '../ESP/Bulletin_board.py'], shell=True)

print("Creacion de Tellers")
teller_processes = []
for i in range(NT):
    process = subprocess.Popen(['start', 'cmd', '/k', 'python', '../Teller/teller.py', '--port', str(5001 + i)], shell=True)
    teller_processes.append(process)

time.sleep(5)

url = "http://127.0.0.1:5000/public-info"
datos={'curve': curve_json, 'g': [gx,gy], 'h': [hx,hy], 'p': p}
respuesta = requests.post(url, json=datos)

for i in range(NT):
    url="http://127.0.0.1:500"+str(i+1)+"/post-info"
    respuesta=requests.post(url,curve_json)

time.sleep(5)
print("VOTANTES, PUEDEN VOTAR\n\n\n")
# Función para ejecutar voter.py
def run_voter(voter_id):
    subprocess.run(['python', '../Voter/voter.py', '--id', str(voter_id), '--NT', str(NT), '--NTH', str(NTH), '--NC', str(NC)])

# Ejecutar voter.py en paralelo, de 10 en 10
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(run_voter, voter_id + 1) for voter_id in range(NV)]
    for future in as_completed(futures):
        future.result()  # Esperar a que cada tarea termine

print('\nTodos los votantes votaron')

time.sleep(1)

print('\nInicio de etapa de conteo')
tellersHonestos= random.sample(range(1,NT+1),NTH)
print(f'Tellers honestos son = {tellersHonestos}')

respuestas=[]
tellers=[]
for i in tellersHonestos:
    url = "http://localhost:500"+str(i)+"/aggregate"
    respuesta = requests.get(url)
    respuestas.append(respuesta.json()['aggregate'])
    tellers.append(respuesta.json()['id'])
    print(f'Obteniendo agregados de Teller {i}')

print(f'Obtencion de los agregados terminada')

print(f'Calculo de la cantidad de votos')

time.sleep(2)
votos=[0]*NC
for i in range(len(tellers)):
    respuesta=respuestas[i]
    teller=tellers[i]
    for cand in respuesta:
        Tj= respuesta[cand]['H']
        L=Fraction(1,1)
        for l in tellers:
            if l!= teller:
                Prod=l
                Div=l-teller
                L*=Fraction(Prod,Div)
        votos[int(cand)]+= int(Tj) * L

print("\n\n\n\nRESULTADO FINAL\n")
print(Q)
print() 
for i in range(len(NN)):
    print(f'{NN[i]}: {int(float(votos[i]))-NV} votos')

_=input()

# Cerrar procesos por nombre de script
print("\nCerrando terminales auxiliares")
def cerrar_procesos(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and script_name in " ".join(cmdline):  # Verifica que cmdline no sea None
                proc.terminate()  # O usa proc.kill() si no quieres esperar
                #print(f"Proceso {script_name} (PID {proc.info['pid']}) terminado.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue



# Cerrar terminales de los tellers
for i in range(NT):
    port = 5001 + i
    cerrar_procesos(f'teller.py --port {port}')

# Cerrar terminal del Bulletin Board
cerrar_procesos('Bulletin_board.py')