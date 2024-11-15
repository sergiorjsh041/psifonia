import requests

# la informacion es pasada por teller 1 y 3

respuestas=[]
tellers = [1,2,4]

url = "http://localhost:5001/aggregate"
respuesta1 = requests.get(url)
print(respuesta1.json())
respuestas.append(respuesta1.json())

url = "http://localhost:5002/aggregate"
respuesta2 = requests.get(url)
print(respuesta2.json())
respuestas.append(respuesta2.json())

url = "http://localhost:5004/aggregate"
respuesta4 = requests.get(url)
print(respuesta4.json())
respuestas.append(respuesta4.json())

Ta=0
Tb=0

for id in range(len(tellers)):
    TjA=respuestas[id]['A']['H']
    TjB=respuestas[id]['B']['H']
    Prod=1
    Div=1
    for l in range(len(tellers)):
        if l!=id:
            Prod*=tellers[l]
            Div*=tellers[l]-tellers[id]
    Ta+=TjA*Prod/Div
    Tb+=TjB*Prod/Div
    
print(f'Votos para candidato A = {Ta}\nVoros para candidato B = {Tb}')



