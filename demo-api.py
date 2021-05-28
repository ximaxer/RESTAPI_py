##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   Nuno Antunes <nmsa@dei.uc.pt>
##   BD 2021 Team - https://dei.uc.pt/lei/
##   University of Coimbra


from flask import Flask, jsonify, request
import logging
import psycopg2
import time
import numpy
import jwt
import datetime
import traceback

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    Hello World!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2021 Team<br/>
    <br/>
    """


##
##      Demo GET
##
## Obtain all departments, in JSON format
##
## To use it, access:
##
##   http://localhost:8080/departments/
##

# REGISTAR NOVO UTILIZADOR
@app.route("/registo/", methods=['POST'])
def register():
    payload = request.get_json()
    conn = db_connection()
    cur2 = conn.cursor()

    statement = """INSERT INTO individuo (username, email, password) VALUES ( %s,   %s ,   %s )"""
    values = (payload["username"], payload["email"], payload["password"])

    cur1 = conn.cursor()
    cur1.execute("SELECT username FROM individuo where username = %s", (values[0],))
    rows = cur1.fetchall()
    if not rows:
        try:
            cur2.execute(statement, values)
            cur2.execute("commit")
            result = 'Inserted!'
        except (Exception, psycopg2.DatabaseError) as error:
            # logger.error(error)
            traceback.print_exc()
            result = 'Failed!'
    else:
        result = 'Failed'
    if conn is not None:
        conn.close()
    return jsonify(result)

# EFETUAR LOGIN
@app.route("/login/", methods=['POST'])
def login():
    payload = request.get_json()
    info = ['','','']
    conn = db_connection()
    cur1 = conn.cursor()
    cur1.execute("SELECT username, email, password FROM individuo where username = %s", (payload['username'],))
    rows = cur1.fetchall()
    if not rows or rows[0][2] != payload['password']:
        result = 'Failed!'
        if conn is not None:
            conn.close()
        return jsonify(result)
    else:
        info[0] = rows[0][0]
        info[1] = rows[0][1]
        info[2] = rows[0][2]
        key = "secret"
        encoded = jwt.encode({"exp": (datetime.datetime.utcnow() + datetime.timedelta(seconds=120)), "token" : info},
                              key, algorithm="HS256")
        if conn is not None:
            conn.close()
        return jsonify(encoded)

# OBTER LISTA DE UTILIZADORES
@app.route("/individuos/", methods=['GET'], strict_slashes=True)
def get_all_departments():
    # logger.info("###              DEMO: GET /departments              ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, email FROM individuo")
    rows = cur.fetchall()

    payload = []
    # logger.debug("---- departments  ----")
    for row in rows:
        # logger.debug(row)
        content = {'username': row[0], 'email': row[1]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

# ADICIONAR UM NOVO LEILAO
@app.route("/addLeilao/", methods=['POST'])
def add_leilao():
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    key = "secret"
    decoded = jwt.decode(payload["token"], key, algorithms="HS256")
    dados_user=decoded['token']
    dataInicioStr = payload["Data de Inicio"].split("-")
    anoI = int(dataInicioStr[0])
    mesI = int(dataInicioStr[1])
    diaI = int(dataInicioStr[2])
    horaI = int(dataInicioStr[3])
    minI = int(dataInicioStr[4])
    segI = int(dataInicioStr[5])
    dataFimStr = payload["Data de Fim"].split("-")
    anoF = int(dataFimStr[0])
    mesF = int(dataFimStr[1])
    diaF = int(dataFimStr[2])
    horaF = int(dataFimStr[3])
    minF = int(dataFimStr[4])
    segF = int(dataFimStr[5])

    statement = """INSERT INTO leilao_artigo (precominimo, titulo, descricao, data_inicio, data_fim, individuo_username,artigo_artigoid) VALUES ( %s, %s, %s, %s, %s, %s, %s)"""
    values = (float(payload["Preco Minimo"]), payload["Titulo"], payload["Descricao"], datetime.datetime(anoI,mesI,diaI,horaI,minI,segI), datetime.datetime(anoF,mesF,diaF,horaF,minF,segF), dados_user[0],payload["Artigo"])

    print(payload["Preco Minimo"] +" | "+ payload["Titulo"] +" | "+ payload["Descricao"] +" | "+ payload["Artigo"]+" | "+ str(datetime.date(anoI,mesI,diaI)) +" | "+ str(datetime.date(anoF,mesF,diaF)) +" | "+ dados_user[0])
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = "Inserted"
    except (Exception, psycopg2.DatabaseError) as error:
        traceback.print_exc()
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

# OBTER LISTA DE LEILOES
@app.route("/leiloes/", methods=['GET'], strict_slashes=True)
def get_all_auctions():
    # logger.info("###              DEMO: GET /departments              ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT leilaoID, titulo, artigo_artigoid, artigo_highest_bid, individuo_username FROM leilao_artigo")
    rows = cur.fetchall()

    payload = []
    # logger.debug("---- departments  ----")
    for row in rows:
        # logger.debug(row)
        content = {'ID': row[0], 'Titulo': row[1], 'Artigo': row[2], 'Licitacao mais alta': row[3], 'Titular': row[4]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

# OBTER LEILAO ESPECIFICADO DETALHADO
@app.route("/leiloes/<leilaoID>", methods=['GET'])
def get_auction(leilaoID):

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT leilaoID, precominimo, titulo, descricao, data_inicio, data_fim, artigo_artigoid, artigo_highest_bid, individuo_username FROM leilao_artigo where leilaoid = %s", (leilaoID,))
    rows = cur.fetchall()
    row = rows[0]
    content = {'ID': row[0], 'Preco Minimo': row[1], 'Titulo': row[2],
                   'Descricao': row[3], 'Data de Inicio': row[4], 'Data de Fim': row[5],
                   'Artigo': row[6], 'Licitacao mais alta': row[7], 'Titular': row[8]}
    conn.close()
    return jsonify(content)

# ATUALIZAR UM LEILAO
@app.route("/actualizaLeilao/<leilaoID>", methods=['PUT'])
def update_auction(leilaoID):
    # logger.info("###              DEMO: PUT /departments              ###");
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    key = "secret"
    decoded = jwt.decode(content["token"], key, algorithms="HS256")
    dados_user = decoded['token']
    cur1 = conn.cursor()
    cur1.execute("SELECT individuo_username FROM leilao_artigo where individuo_username = %s and leilaoID = %s", (dados_user[0], leilaoID))
    rows = cur1.fetchall()
    if not rows:
        return jsonify('Utilizador nao e o titular deste leilao')

    if "Preco Minimo" not in content or "Titulo" not in content or "Descricao" not in content or \
            "Artigo" not in content or "Data de Inicio" not in content or "Data de Fim" not in content or "token" not in content:
        return jsonify('all fields are required to update')

    dataInicioStr = content["Data de Inicio"].split("-")
    anoI = int(dataInicioStr[0])
    mesI = int(dataInicioStr[1])
    diaI = int(dataInicioStr[2])
    horaI = int(dataInicioStr[3])
    minI = int(dataInicioStr[4])
    segI = int(dataInicioStr[5])
    dataFimStr = content["Data de Fim"].split("-")
    anoF = int(dataFimStr[0])
    mesF = int(dataFimStr[1])
    diaF = int(dataFimStr[2])
    horaF = int(dataFimStr[3])
    minF = int(dataFimStr[4])
    segF = int(dataFimStr[5])
    # parameterized queries, good for security and performance
    statement = """
                UPDATE leilao_artigo 
                  SET precominimo = %s, titulo = %s, descricao = %s, artigo_artigoid = %s, data_inicio = %s, data_fim = %s
                WHERE leilaoID = %s"""

    values = (content["Preco Minimo"], content["Titulo"], content["Descricao"], content["Artigo"], datetime.datetime(anoI,mesI,diaI,horaI,minI,segI), datetime.datetime(anoF,mesF,diaF,horaF,minF,segF), leilaoID)
    print(content["Preco Minimo"]+" | "+content["Titulo"]+" | "+content["Descricao"]+" | "+content["Artigo"]+" | "+content["Data de Inicio"]+" | "+content["Data de Fim"]+" | "+leilaoID)
    try:
        res = cur.execute(statement, values)
        result = f'Updated: {cur.rowcount}'
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        # logger.error(error)
        traceback.print_exc()
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)




##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user="uzxfbjcsgmeotl",
                          password="e5406a37ddb46d97450d27f6b8517ef51e9fcad850873d3ce94ffc60a457f64d",
                          host="ec2-54-155-226-153.eu-west-1.compute.amazonaws.com",
                          port="5432",
                          database="degc9kh8m9bu4j")
    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":
    # Set up the logging
    # logging.basicConfig(filename="logs/log_file.log")
    # logger = logging.getLogger('logger')
    # logger.setLevel(logging.DEBUG)
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)

    # create formatter
    # formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
    #                              '%H:%M:%S')
    # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)

    time.sleep(1)  # just to let the DB start before this print :-)

    #logger.info("\n---------------------------------------------------------------\n" +
    #             "API v1.0 online: http://localhost:8080/departments/\n\n")

    app.run(host="localhost", debug=True, threaded=True)
