from flask import Flask, jsonify, request
import argparse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.exceptions import InvalidSignature
'''
Qué paramatros debo setear? Hay valores predeterminados?
Hay algun tipo de firma especifica? RSA?
Propongo una forma de JSON?
Los votantes se definen por un ID y una clave pública? o necesito la IP?
Cuando llega una request, cómo verifico de qué votante es?, mediante el ID y el mensaje firmado?

funciones que verifiquen firmas
'''

import requests

app = Flask(__name__)

info={"id" : None,
       
      'e': None, 
      'n': None,
      'd': None,
      
      'q': None,
      'g': 3, 
      'h': 5,

      'votantes': None}

Shares = {}
'''
{votante: {A: {G: G, H: H}, B: {G: G, H: H}}
'''

@app.route('/')
def home():
    return jsonify({"message": "¡Hola, Mundo!"})

@app.route('/generate-keys', methods=['POST'])
def generate_keys():
    '''
    Recibe en un JSON su id, el g y el h de la elección, 
    las claves públicas de firma de los votantes, junto con su identificación

    votantes vienen de la forma {id: {e: e, n: n}, ...}
    '''
    datos = request.get_json()
    info["id"] = datos['id']

   
    info['q'] = datos['q']
    info["g"] = datos['g']
    info["h"] = datos['h']
    info["votantes"] = datos['votantes']

    pe = 65537
    sk = rsa.generate_private_key(public_exponent=pe, key_size=2048).private_numbers()
    e=sk.public_numbers.e
    n = sk.public_numbers.n
    d = sk.d

    info['e']= e
    info['n'] = n
    info['d'] = d
    
    return jsonify({"e": info["e"], "n": info["n"]})

@app.route('/commitment', methods=['POST'])
def get_commitment():
    '''
    {i: i, Eval: {j1: {G: Gj1,H: Hj1}, ...}, Sign: sign}
    '''
    datos = request.get_json()
    votante=datos['i']
    Eval = datos['Eval']
    sign = datos['Sign']

    print(f"Obteniendo evaluaciones de votante {votante}")

    # mensaje a validar: i + Gj1 + Hj1 + Gj2 + Hj2 + ...
    msj=votante
    for j in Eval:
        msj+=str(Eval[j]['G'])+str(Eval[j]['H'])
    msj=msj.encode()
     
    # Validar firma

    print(f"Buscando información de votante {votante} en Bulletin Board")

    #bulletin_board[votante]["commitments"] = Eval
    url = "http://localhost:5000/get-public-commitments/"+str(votante) 
    response= requests.get(url)
    data=response.json()
    
    g=int(info['g'])
    h=int(info['h'])
    allverify=True
    print(f"Empezando verificación de evaluaciones del votante {votante}")
    for key in Eval.keys():
        print(f"Key: {key}, Value: {Eval[key]}")
        evaluacion=Eval[key]
        comm=data['commitments'][key]
        id_teller=args.port-5000
        G=evaluacion['G']
        H=evaluacion['H']

        e=0
        value2=1
        for c in range(len(comm)):
            value2*=comm[c]**(id_teller**e)
            e+=1
        verify= g**G*h**H==value2
        if verify:
            print(f"Voto de votante {votante} para candidato {key} verificado")
        else:
            print("falla de verificacion")
            print(f'{g**G*h**H} != {value2}')
            allverify = False
    if allverify:
        print("Todas las verificaciones exitosas")
        print(f"Guardando {Eval}")
        Shares[votante]=Eval
        return(jsonify("Todo verificado, guardado!"))
    else:
        return(jsonify("falla de verificación"))

#@app.route('/verify-associations', methods=['POST'])

@app.route('/aggregate', methods=['GET'])
def aggregate():
    '''
    Recibe un JSON con la lista de votantes y sus votos
    '''
    print("\n\n\nEmpezando agregación y envío")

    aggregates=dict()
    nc=0
    for votante in Shares:
        for cand in Shares[votante]:
            nc+=1
        break
    print(f'Numero de candidatos = {nc}')

    for i in range(nc):
        aggregates[i] = {"G": 0, "H":0}
    
    for votante in Shares:
        for cand in Shares[votante]:
            aggregates[int(cand)]["G"]+= Shares[votante][cand]["G"]
            aggregates[int(cand)]["H"]+= Shares[votante][cand]["H"]
    
    print(f'agregados finales = {aggregates}')
    
    print("Envio realizado")
    return jsonify({"id": args.port-5000, "aggregate": aggregates})


@app.route('/get-info', methods=['GET'])
def get_info():
    return jsonify(info)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Inicia el servidor Flask en un puerto específico.")
    parser.add_argument('--port', type=int, default=5000, help="Puerto para la API de Flask (por defecto es 5000)")
    args = parser.parse_args()
    
    app.run(debug=True, port=args.port)