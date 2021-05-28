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
        encoded = jwt.encode({"exp": (datetime.datetime.utcnow() + datetime.timedelta(minutes=30)), "token" : info},
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


# OBTER LISTA DE NOTIFICACOES
@app.route("/notificacoes/", methods=['GET'], strict_slashes=True)
def get_all_notifications():
    # logger.info("###              DEMO: GET /departments              ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT mensagemID, texto, individuo_username  FROM mensagem where privado = True and data_leitura is null")
    rows = cur.fetchall()

    payload = []
    # logger.debug("---- departments  ----")
    for row in rows:
        # logger.debug(row)
        content = {'ID': row[0], 'notificacao': row[1], 'user': row[2],}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


# OBTER LISTA DE VERSOES
@app.route("/versions/leilaoID", methods=['GET'], strict_slashes=True)
def get_all_versions(leilaoID):
    # logger.info("###              DEMO: GET /departments              ###");

    conn = db_connection()
    cur = conn.cursor()


    cur.execute("SELECT data_de_alteracao, precominimo, titulo, descricao, data_inicio, data_inicio, artigo_artigoid  FROM versao where leilao_leilaoid = %s",(leilaoID,))
    rows = cur.fetchall()

    payload = []
    # logger.debug("---- departments  ----")
    for row in rows:
        # logger.debug(row)
        content = {'Alterado a': row[0], 'Preco minimo': row[1], 'Titulo': row[2], 'Descricao': row[3], 'Data de inicio': row[4], 'Data de fim': row[5], 'Artigo': row[6]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

# OBTER NOTIFICACOES DO UTLIZADOR
@app.route("/notificacoesUser/", methods=['PUT'], strict_slashes=True)
def get_user_notifications():
    content = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    key = "secret"
    decoded = jwt.decode(content["token"], key, algorithms="HS256")
    dados_user = decoded['token']

    cur.execute("SELECT mensagemID, texto  FROM mensagem where privado = True and data_leitura is null and individuo_username = %s", (dados_user[0],))
    rows = cur.fetchall()

    payload = []
    for row in rows:
        content = {'notificacao': row[1]}
        payload.append(content)  # appending to the payload to be returned

        statement = """
                    UPDATE mensagem 
                    SET data_leitura = %s
                    WHERE mensagemID = %s"""

        values = (datetime.datetime.now(),row[0])
        try:
            cur.execute(statement, values)
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            # logger.error(error)
            traceback.print_exc()
            result = 'Failed!'
            if conn is not None:
                conn.close()
            return jsonify(result)
    if conn is not None:
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

    cur.execute("SELECT leilaoid, descricao FROM leilao_artigo")
    rows = cur.fetchall()

    payload = []
    # logger.debug("---- departments  ----")
    for row in rows:
        # logger.debug(row)
        content = {'ID': row[0], 'Descricao': row[1]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

# OBTER LISTA DE LEILOES POR ARTIGO
@app.route("/leiloes/<artigo>", methods=['GET'], strict_slashes=True)
def get_auctions_by_item(artigo):
    # logger.info("###              DEMO: GET /departments              ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT leilaoid, descricao FROM leilao_artigo where artigo_artigoid = %s", (artigo,))
    rows = cur.fetchall()

    payload = []
    # logger.debug("---- departments  ----")
    for row in rows:
        # logger.debug(row)
        content = {'ID': row[0], 'Descricao': row[1]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

# OBTER LEILAO ESPECIFICADO DETALHADO
@app.route("/leilao/<leilaoID>", methods=['GET'])
def get_auction(leilaoID):

    conn = db_connection()
    curLeilao = conn.cursor()
    curMensagem = conn.cursor()
    curLicitacao = conn.cursor()

    curLeilao.execute("SELECT leilaoID, precominimo, titulo, descricao, data_inicio, data_fim, artigo_artigoid, artigo_highest_bid, individuo_username FROM leilao_artigo where leilaoid = %s", (leilaoID,))
    curMensagem.execute("SELECT mensagemID, texto, individuo_username FROM mensagem WHERE privado = false and leilao_leilaoid = %s", (leilaoID,))
    curLicitacao.execute("SELECT licitacaoid, valorlicitado, individuo_username FROM licitacao WHERE leilao_leilaoid = %s", (leilaoID,))
    rowsLeilao = curLeilao.fetchall()
    rowsMensagem = curMensagem.fetchall()
    rowsLicitacao = curLicitacao.fetchall()

    rowLeilao = rowsLeilao[0]
    content = {'ID': rowLeilao[0], 'Titulo':rowLeilao[2], 'Descricao': rowLeilao[3], 'Data de Inicio': rowLeilao[4], 'Data de Fim': rowLeilao[5],
                   'Artigo': rowLeilao[6], 'Licitacao mais alta': rowLeilao[7], 'Titular': rowLeilao[8],"Mensagens":[], "Licitacoes":[]}
    for x in rowsMensagem:
        content["Mensagens"].append(str(x[0]) + " " + x[1] + " " + x[2]+"\n")
    for y in rowsLicitacao:
        content["Licitacoes"].append(str(y[0]) + " " + str(y[1]) + " " + y[2] + "\n")
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
    cur2 = conn.cursor()
    cur1.execute("SELECT precominimo, titulo, descricao, artigo_artigoid, data_inicio, data_fim, individuo_username FROM leilao_artigo where individuo_username = %s and leilaoid = %s", (dados_user[0], leilaoID))
    rows = cur1.fetchall()
    if rows[0][5] < datetime.datetime.now():
        return jsonify('This auction has already finished')
    if not rows:
        return jsonify('Utilizador nao e o titular deste leilao')

    if "Preco Minimo" not in content or "Titulo" not in content or "Descricao" not in content or \
            "Artigo" not in content or "Data de Inicio" not in content or "Data de Fim" not in content or "token" not in content:
        return jsonify('all fields are required to update')


    dados_leilao = [rows[0][0], rows[0][1], rows[0][2], rows[0][3], (rows[0][4]).strftime("%m-%d-%Y-H-%M-%S"), rows[0][5].strftime("%m-%d-%Y-H-%M-%S")]
    print(dados_leilao)
    statement = ("""INSERT INTO versao (data_de_alteracao, precominimo, titulo, descricao, artigo_artigoid, data_inicio, data_fim, leilao_leilaoid)  VALUES ( %s, %s, %s,%s, %s, %s,%s, %s)""")
    valores = (datetime.datetime.now(), rows[0][0], rows[0][1], rows[0][2], rows[0][3], (rows[0][4]), rows[0][5], leilaoID)
    try:
        cur2.execute(statement, valores)
        cur2.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        traceback.print_exc()
        result = 'Failed to insert version!'
        return jsonify(result)

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
                WHERE leilaoid = %s"""

    values = (content["Preco Minimo"], content["Titulo"], content["Descricao"], content["Artigo"], datetime.datetime(anoI,mesI,diaI,horaI,minI,segI), datetime.datetime(anoF,mesF,diaF,horaF,minF,segF), leilaoID)
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

# EFETUAR UMA LICITACAO

@app.route("/licitar/<leilaoID>/<valorLicitacado>", methods=['POST'])
def bid(leilaoID,valorLicitacado):
    payload = request.get_json()
    conn = db_connection()
    key = "secret"
    decoded = jwt.decode(payload["token"], key, algorithms="HS256")
    dados_user = decoded['token']
    curLeilao = conn.cursor()
    curLicita = conn.cursor()
    curNotif = conn.cursor()
    curAux = conn.cursor()
    curLeilao.execute("SELECT precominimo, artigo_highest_bid, data_fim, individuo_username FROM leilao_artigo where leilaoid = %s", (leilaoID))
    rows = curLeilao.fetchall()
    print(rows)
    curAux.execute("SELECT valorlicitado from licitacao where licitacaoid = %s", (rows[0][1],))
    valorMaisAlto = curAux.fetchall()
    print(valorMaisAlto)
    if dados_user[0] == rows[0][3]:
        return jsonify('The owner of an auction cannot bid on his own auction!')
    if datetime.datetime.now() > rows[0][2]:
        return jsonify('This auction has expired!')
    if rows[0][1] is not None:
        if float(valorLicitacado) > float(valorMaisAlto[0][0]):
            statement = ("""INSERT INTO licitacao (valorlicitado, individuo_username, leilao_leilaoid)  
            VALUES ( %s, %s, %s)""")
            valores = (valorLicitacado, dados_user[0], leilaoID)
            try:
                curLicita.execute(statement, valores)
                curLicita.execute("commit")
                curLicita.execute("SELECT licitacaoid FROM licitacao WHERE leilao_leilaoid = %s and valorlicitado = %s", (leilaoID, valorLicitacado))
                rows=curLicita.fetchall()
                licitacaoID=rows[0][0]
            except (Exception, psycopg2.DatabaseError) as error:
                traceback.print_exc()
                result = 'Failed to insert auction!'
                if conn is not None:
                    conn.close()
                return jsonify(result)
        else:
            if conn is not None:
                conn.close()
            return jsonify('Your bid is too low!')
    else:
        if float(valorLicitacado) > float(rows[0][0]):
            statement = ("""INSERT INTO licitacao (valorlicitado, individuo_username, leilao_leilaoid)  
            VALUES ( %s, %s, %s)""")
            valores = (valorLicitacado, dados_user[0], leilaoID)
            try:
                curLicita.execute(statement, valores)
                curLicita.execute("commit")
                curLicita.execute("SELECT licitacaoid FROM licitacao WHERE leilao_leilaoid = %s and valorlicitado = %s",(leilaoID, valorLicitacado))
                rows = curLicita.fetchall()
                licitacaoID = rows[0][0]
            except (Exception, psycopg2.DatabaseError) as error:
                traceback.print_exc()
                result = 'Failed to insert auction!'
                if conn is not None:
                    conn.close()
                return jsonify(result)
        else:
            if conn is not None:
                conn.close()
            return jsonify('Your bid is too low!')
    statement = """UPDATE leilao_artigo SET artigo_highest_bid = %s WHERE leilaoid = %s"""
    values = (licitacaoID,leilaoID)
    try:
        curLeilao.execute(statement, values)
        curLeilao.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        traceback.print_exc()
        if conn is not None:
            conn.close()
        return jsonify('Failed updating auction!')
    curNotif.execute("SELECT DISTINCT individuo_username FROM licitacao WHERE leilao_leilaoid = %s and valorlicitado < %s", (leilaoID, valorLicitacado))
    rows = curNotif.fetchall()
    for x in rows:
        if x[0] == dados_user[0]:
            continue
        statement = ("""INSERT INTO mensagem(texto,privado,leilao_leilaoid,individuo_username)
        VALUES (%s,%s,%s,%s)""")
        notificacao = "Licitacao ultrapassada no leilao "+leilaoID+"!"
        #print(notificacao +" 1 "+ leilaoID +" "+ x[0])
        values = (notificacao, True, leilaoID, x[0])
        curNotif.execute(statement, values)
    return jsonify('success')


#Listar	todos	os	leiloes	em	que	o	utilizador	tenha	atividade
@app.route("/listar/", methods=['GET'])
def get_auctions():
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    key = "secret"
    decoded = jwt.decode(payload["token"], key, algorithms="HS256")
    dados_user = decoded['token']

    cur.execute(
        "SELECT leilaoid, titulo, descricao, artigo_artigoid  FROM leilao_artigo where individuo_username = %s", (dados_user[0],))
    rows = cur.fetchall()

    payload = []
    for row in rows:
        # logger.debug(row)
        content = {'leilaoid': row[0], 'titulo': row[1], 'descricao': row[2], 'artigo id': row[3]}
        payload.append(content)  # appending to the payload to be returned

    cur.execute(
        "SELECT leilao_leilaoid FROM licitacao where individuo_username = %s",
        (dados_user[0],))
    rows = cur.fetchall()

    for row in rows:
        cur.execute(
            "SELECT leilaoid, titulo, descricao, artigo_artigoid  FROM leilao_artigo where leilaoid = %s",
            (row[0],))
        row2 = cur.fetchall()
        content = {'leilaoid': row2[0][0], 'titulo': row2[0][1], 'descricao': row2[0][2], 'artigo id': row2[0][3]}
        payload.append(content)  # appending to the payload to be returned
    conn.close()
    return jsonify(payload)

@app.route("/mural/<leilaoID>", methods=['POST'])
def write_on_mural(leilaoID):
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    key = "secret"
    decoded = jwt.decode(payload["token"], key, algorithms="HS256")
    dados_user=decoded['token']

    statement = """INSERT INTO mensagem (texto, leilao_leilaoid, individuo_username) VALUES ( %s, %s, %s)"""
    values = (payload["Texto"], leilaoID, dados_user[0])

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = "Inserted"
    except (Exception, psycopg2.DatabaseError) as error:
        traceback.print_exc()
        result = 'Failed!'
        if conn is not None:
            conn.close()
        return jsonify(result)
    cur.execute("SELECT DISTINCT individuo_username FROM mensagem WHERE leilao_leilaoid = %s and privado = false", (leilaoID,))
    listaUsers = cur.fetchall()
    message = "New message on auction "+leilaoID
    for individuo in listaUsers:
        if individuo[0] == dados_user[0]:
            continue
        try:
            statement = """INSERT INTO mensagem (texto, leilao_leilaoid, individuo_username, privado) VALUES ( %s, %s, %s, true)"""
            values = (message, leilaoID, individuo[0])
            cur.execute(statement, values)
            cur.execute("commit")
        except(Exception, psycopg2.DatabaseError) as error:
            traceback.print_exc()
            result = 'Failed!'
            if conn is not None:
                conn.close()
            return jsonify(result)
    cur.execute("SELECT individuo_username from leilao_artigo where leilaoid = %s",(leilaoID,))
    owner = cur.fetchall()
    statement = """INSERT INTO mensagem (texto, leilao_leilaoid, individuo_username, privado) VALUES ( %s, %s, %s, true)"""
    values = (message, leilaoID, owner[0][0])
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = "Message Posted"
    except(Exception, psycopg2.DatabaseError) as error:
        traceback.print_exc()
        result = 'Failed!'
        if conn is not None:
            conn.close()
        return jsonify(result)
    if conn is not None:
        conn.close()
    return jsonify(result)

@app.route("/fimLeilao/<leilaoID>", methods=['POST'])
def close_auction(leilaoID):
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    key = "secret"
    decoded = jwt.decode(payload["token"], key, algorithms="HS256")
    dados_user=decoded['token']

    cur.execute(
        "SELECT data_fim, individuo_username, artigo_highest_bid  FROM leilao_artigo where leilaoid = %s", (leilaoID))
    rows = cur.fetchall()
    if datetime.datetime.now() < rows[0][0]:
        return jsonify('This auction is still ongoing!')
    if dados_user[0] != rows[0][1]:
        return jsonify('Only the owner of the auction can close it!')
    cur.execute("SELECT individuo_username, valorlicitado FROM licitacao WHERE licitacaoid = %s", (rows[0][2],))
    winner = cur.fetchall()
    cur.execute( "SELECT DISTINCT individuo_username FROM licitacao WHERE leilao_leilaoid = %s", (leilaoID))
    individuos = cur.fetchall()
    message = "User " + winner[0][0] + " won the auction with a bid of " + str(winner[0][1])
    for individuo in individuos:
        statement = """INSERT INTO mensagem (texto, leilao_leilaoid, individuo_username, privado) VALUES ( %s, %s, %s, true)"""
        values = (message, leilaoID, individuo[0])
        try:
            cur.execute(statement, values)
            cur.execute("commit")
        except(Exception, psycopg2.DatabaseError) as error:
            traceback.print_exc()
            result = 'Failed!'
            if conn is not None:
                conn.close()
            return jsonify(result)
    if conn is not None:
        conn.close()
    return jsonify('Message sent')

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
