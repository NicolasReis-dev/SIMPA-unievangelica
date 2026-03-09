# Arquivo: app.py

import csv
import logging
from flask import Flask, jsonify
from models.aluno import Aluno # Importando a classe

# SETUP DO LOG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger("SIMPA_API")

app = Flask(__name__)

# Banco de dados em memória
banco_de_alunos = []

def carregar_dados_csv():
    """Lê o arquivo CSV e converte em objetos Orientados a Objetos."""
    try:
        with open('data/alunos.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                # Cria o objeto Aluno
                aluno = Aluno(matricula=linha['matricula'], nome=linha['nome'])
                # Insere as notas e faltas usando os métodos da classe
                aluno.adicionar_nota(float(linha['nota_1']))
                aluno.adicionar_nota(float(linha['nota_2']))
                aluno.registrar_faltas(int(linha['faltas']))
                
                banco_de_alunos.append(aluno)
        logger.info(f"Sucesso: {len(banco_de_alunos)} alunos carregados do CSV.")
    except Exception as e:
        logger.error(f"Erro ao ler o CSV: {e}")

# Executa o carregamento antes do servidor ligar
carregar_dados_csv()

# ROTAS
@app.route('/', methods=['GET'])
def index():
    logger.info("Acessaram a rota principal.")
    return jsonify({"sistema": "SIMPA - UniEVANGÉLICA", "status": "Online"})

@app.route('/alunos', methods=['GET'])
def listar_alunos():
    """Retorna os dados dos alunos no formato JSON."""
    logger.info("Solicitação GET /alunos recebida.")
    
    alunos_json = []
    for aluno in banco_de_alunos:
        alunos_json.append({
            "matricula": aluno.matricula,
            "nome": aluno.nome,
            "media_atual": round(aluno.calcular_media(), 2),
            "faltas": aluno.faltas,
            "risco_evasao": aluno.risco
        })
        
    return jsonify({"total_alunos": len(alunos_json), "alunos": alunos_json})

if __name__ == '__main__':
    logger.info("Iniciando o servidor do SIMPA na porta 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)