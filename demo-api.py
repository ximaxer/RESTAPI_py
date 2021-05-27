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


##
##      Demo GET
##
## Obtain department with ndep <ndep>
##
## To use it, access:
##
##   http://localhost:8080/departments/10
##

@app.route("/leilao/<leilaoID>", methods=['GET'])
def get_leilao(leilaoID):
    # logger.info("###              DEMO: GET /departments/<ndep>              ###");

    # logger.debug(f'ndep: {ndep}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT leilaoid, individuo_username, titulo, descricao, precominimo,"
                " artigo_artigoid, artigo_highest_bid, data_inicio, data_fim,"
                " FROM leilao_artigo where leilaoid = %s", (leilaoID,))
    rows = cur.fetchall()
    row = rows[0]
    content = {'leilaoid': int(row[0]), 'titular': row[1], 'titulo': row[2], 'descricao': row[3],
               'preco minimo': float(row[4]), 'ID artigo': int(row[5]), 'oferta mais alta': float(row[6]), 'data de inicio': row[7], 'data de fim': row[8]}

    conn.close()
    return jsonify(content)


##
##      Demo POST
##
## Add a new department in a JSON payload
##
## To use it, you need to use postman or curl:
##
##   curl -X POST http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"localidade": "Polo II", "ndep": 69, "nome": "Seguranca"}'
##


@app.route("/departments/", methods=['POST'])
def add_departments():
    # logger.info("###              DEMO: POST /departments              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    # logger.info("---- new department  ----")
    # logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO dep (ndep, nome, local) 
                          VALUES ( %s,   %s ,   %s )"""

    values = (payload["ndep"], payload["localidade"], payload["nome"])
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Inserted!'
    except (Exception, psycopg2.DatabaseError) as error:
        # logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


##
##      Demo PUT
##
## Update a department based on the a JSON payload
##
## To use it, you need to use postman or curl:
##
##   curl -X PUT http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"ndep": 69, "localidade": "Porto"}'
##

@app.route("/departments/", methods=['PUT'])
def update_departments():
    # logger.info("###              DEMO: PUT /departments              ###");
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    # if content["ndep"] is None or content["nome"] is None :
    #    return 'ndep and nome are required to update'

    if "ndep" not in content or "localidade" not in content:
        return 'ndep and localidade are required to update'

    # logger.info("---- update department  ----")
    # logger.info(f'content: {content}')

    # parameterized queries, good for security and performance
    statement = """
                UPDATE dep 
                  SET local = %s
                WHERE ndep = %s"""

    values = (content["localidade"], content["ndep"])

    try:
        res = cur.execute(statement, values)
        result = f'Updated: {cur.rowcount}'
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        # logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

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
            result = 'Failed!'
    else:
        result = 'Failed'
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
