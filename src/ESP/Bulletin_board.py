from flask import Flask, jsonify, request

app = Flask(__name__)

pbb={}

@app.route('/public_commitments', methods=['POST'])
def publicar():
    '''
    datos={'id': 5, 'commitments': {j1:{B, B1, B2,... }, ...}, wfp: {wfp1, wfp2, ...}, sign: sign}
    '''
    datos = request.get_json()
    info={}
    info['commitments'] = datos['commitments']
    info['wfp'] = datos['wfp']
    info['sign'] = datos['sign']
    pbb[datos['id']]=info
    return jsonify({"message": "Publicado"})

@app.route('/get-public-commitments/<id>', methods=['GET'])
def get_public_commitments(id):
    return jsonify(pbb[id])


if __name__ == '__main__':
    app.run(debug=True, port=5000)