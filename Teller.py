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
    print("commitment")
    datos = request.get_json()
    votante=datos['i']
    Eval = datos['Eval']
    sign = datos['Sign']

    # mensaje a validar: i + Gj1 + Hj1 + Gj2 + Hj2 + ...
    msj=votante
    for j in Eval:
        msj+=str(Eval[j]['G'])+str(Eval[j]['H'])
    msj=msj.encode()
     
    # Validar firma

    #bulletin_board[votante]["commitments"] = Eval

    url = "http://localhost:5000/get-public-commitments/"+str(votante)
    response= requests.get(url)
    data=response.json()
    
    g=int(info['g'])
    h=int(info['h'])

    #votante A
    EvalA=Eval['A']
    Comm=data['commitments']['A']
    id_teller=args.port-5000
    GA= EvalA['G']
    HA= EvalA['H']
    
    BA= Comm['B']
    BA1= Comm['B1']
    BA2= Comm['B2']

    verifyA=g**GA * h**HA== BA * BA1**(id_teller) * BA2**(id_teller**2)
    if verifyA:
        print("Voto A verificado")

    #votante B
    EvalB=Eval['B']
    Comm=data['commitments']['B']
    GB= EvalB['G']
    HB= EvalB['H']

    BB= Comm['B']
    BB1= Comm['B1']
    BB2= Comm['B2']
    
    verifyB=g**GB * h**HB== BB * BB1**(id_teller) * BB2**(id_teller**2)
    if verifyB:
        print("Voto B verificado")

    if verifyA and verifyB:
        Shares[votante]=Eval
        return jsonify({"message": "Voto completo verificado"})

    return jsonify({"verifyA": verifyA, "verifyB": verifyB})
#@app.route('/verify-associations', methods=['POST'])

@app.route('/aggregate', methods=['GET'])
def aggregate():
    '''
    Recibe un JSON con la lista de votantes y sus votos
    '''
    print("aggregate")
    Agg_GA=Agg_HA= Agg_GB= Agg_HB=0
    
    for votante in Shares:
        Agg_GA+=Shares[votante]['A']['G']
        Agg_HA+=Shares[votante]['A']['H']
        Agg_GB+=Shares[votante]['B']['G']
        Agg_HB+=Shares[votante]['B']['H']
    
    return jsonify({"id": args.port-5000,"A": {"G": Agg_GA, "H": Agg_HA}, "B": {"G": Agg_GB, "H": Agg_HB}})


@app.route('/get-info', methods=['GET'])
def get_info():
    return jsonify(info)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Inicia el servidor Flask en un puerto específico.")
    parser.add_argument('--port', type=int, default=5000, help="Puerto para la API de Flask (por defecto es 5000)")
    args = parser.parse_args()
    
    app.run(debug=True, port=args.port)