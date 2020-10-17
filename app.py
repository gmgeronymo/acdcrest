# API REST para buscar leituras no banco de dados 'Resultados.mdb'

# Autor: Gean Marcos Geronymo
# Data inicial: 10/10/2020

# Dados do programa
__version__="0.1"
__date__="10/10/2020"
__appname__="acdcRest"
__author__="Gean Marcos Geronymo"
__author_email__="gean.geronymo@gmail.com"

# carregar bibliotecas
import configparser  # abrir arquivos de configuracao (.ini)
import pandas as pd # pandas - dataframe
import pyodbc # modulo pyodbc: acesso ao DB Access
from flask import Flask,jsonify,request,abort # flask web server

# carregar configuracoes do arquivo settings.ini
config = configparser.ConfigParser()
config.read('settings.ini')
# buscar caminho e passwd de arquivo de configuracao
caminhoTensao = config['BancoResultados']['caminhoTensao']
caminhoCorrente = config['BancoResultados']['caminhoCorrente']
passwd = config['BancoResultados']['password']

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():

    if request.method == 'POST':
        # recebe nome do registro e grandeza por POST

        if not request.json or not 'nome' in request.json:
            abort(400)
        else :
            nome = request.json['nome']

        if not request.json or not 'grandeza' in request.json:
            abort(400)
        else :
            grandeza = request.json['grandeza']

        if grandeza == 'tensao':
            caminho = caminhoTensao
        else:
            caminho = caminhoCorrente

        # chama a funcao buscar_leituras
        db_data = buscar_leituras(caminho,nome,passwd)

        tb_resultados = db_data[0].to_dict()
        tb_padraoinf = db_data[1].to_dict()
        tb_valmed = db_data[2].to_dict()
        tb_leituras = db_data[3].to_dict()
    
        return jsonify(tb_resultados=tb_resultados,tb_padraoinf=tb_padraoinf,tb_valmed=tb_valmed,tb_leituras=tb_leituras)


# busca leituras no banco de dados MS ACCESS
def buscar_leituras(caminhoBancoDados, nomeRegistro, passwd):
    conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}; DBQ='+caminhoBancoDados+'Resultados.mdb;PWD='+passwd)
    with conn:
        query = "SELECT * FROM Resultados WHERE NOMEREG='"+nomeRegistro+"'"
        tb_resultados = pd.read_sql_query(query,conn)

        codreg = tb_resultados.loc[0,'CODREG']
        codpad = tb_resultados.loc[0,'CODPAD']

        query = "SELECT * FROM Valmed WHERE CODREG="+str(codreg)
        tb_valmed = pd.read_sql_query(query,conn)
        tb_valmed['HORACAL'] = pd.to_datetime(tb_valmed['HORACAL']).dt.time
        tb_valmed.loc[:,'DATACAL'] = pd.to_datetime(tb_valmed.HORACAL.astype(str)+' '+tb_valmed.HORACAL.astype(str))
        tb_valmed = tb_valmed.drop(columns=['HORACAL'])

        query = "SELECT * FROM Leituras WHERE CODREG="+str(codreg)
        tb_leituras = pd.read_sql_query(query,conn)

    conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}; DBQ='+caminhoBancoDados+'Padroes.mdb;PWD='+passwd)
    with conn:
        query = "SELECT * FROM PadraoInf WHERE CODPAD="+str(codpad)
        tb_padraoinf = pd.read_sql_query(query,conn)
    
    output = []
    output.append(tb_resultados)
    output.append(tb_padraoinf)
    output.append(tb_valmed)
    output.append(tb_leituras)
    
    return output


