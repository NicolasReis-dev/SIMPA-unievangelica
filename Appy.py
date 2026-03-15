# Arquivo: app.py

import csv
import logging
from flask import Flask, jsonify, request
from models.aluno import Aluno  # Importando a classe

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


@app.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    """Cadastra um novo aluno no sistema."""
    logger.info("Solicitação POST /alunos recebida.")

    dados = request.get_json()

    # Validação para não quebrar o servidor
    if not dados or 'matricula' not in dados or 'nome' not in dados:
        return jsonify({"erro": "Dados incompletos. Matrícula e nome são obrigatórios."}), 400

    try:
        # Usa a nossa classe POO
        novo_aluno = Aluno(matricula=dados['matricula'], nome=dados['nome'])

        if 'nota_1' in dados: novo_aluno.adicionar_nota(float(dados['nota_1']))
        if 'nota_2' in dados: novo_aluno.adicionar_nota(float(dados['nota_2']))
        if 'faltas' in dados: novo_aluno.registrar_faltas(int(dados['faltas']))

        banco_de_alunos.append(novo_aluno)
        logger.info(f"Aluno {novo_aluno.nome} cadastrado com sucesso!")

        return jsonify({"mensagem": "Aluno cadastrado com sucesso!", "risco_evasao": novo_aluno.risco}), 201

    except Exception as e:
        logger.error(f"Erro ao cadastrar: {e}")
        return jsonify({"erro": "Erro interno do servidor."}), 500


if __name__ == '__main__':
    logger.info("Iniciando o servidor do SIMPA na porta 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)