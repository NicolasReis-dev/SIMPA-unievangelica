# Arquivo: app.py

import os
import logging
import pandas as pd
from flask import Flask, jsonify, request
from models.aluno import Aluno  # Importando a nossa classe

# SETUP DO LOG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger("SIMPA_API")

app = Flask(__name__)

# Caminho absoluto para o banco de dados
ARQUIVO_CSV = os.path.join('data', 'alunos.csv')

# ROTAS


@app.route('/', methods=['GET'])
def index():
    logger.info("Acessaram a rota principal.")
    return jsonify({"sistema": "SIMPA - UniEVANGÉLICA", "status": "Online"})


@app.route('/alunos', methods=['GET'])
def listar_alunos():
    """Retorna os dados dos alunos lendo diretamente do CSV com Pandas."""
    logger.info("Solicitação GET /alunos recebida.")
    try:
        # O Pandas lê o arquivo CSV inteiro de uma vez
        df_alunos = pd.read_csv(ARQUIVO_CSV)

        # Converte a tabela do Pandas direto para o formato JSON do Flask
        return jsonify({
            "total_alunos": len(df_alunos),
            "alunos": df_alunos.to_dict(orient='records')
        }), 200
    except Exception as e:
        logger.error(f"Erro ao ler o CSV: {e}")
        return jsonify({"erro": f"Falha ao ler o banco de dados: {str(e)}"}), 500


@app.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    """Cadastra um novo aluno no sistema, calcula o risco com POO e salva no disco."""
    logger.info("Solicitação POST /alunos recebida.")

    dados = request.get_json()

    # Validação para não quebrar o servidor
    if not dados or 'matricula' not in dados or 'nome' not in dados:
        return jsonify({"erro": "Dados incompletos. Matrícula e nome são obrigatórios."}), 400

    try:
        # 1. Usa a nossa classe POO para calcular a média e o risco
        novo_aluno = Aluno(matricula=dados['matricula'], nome=dados['nome'])

        nota_1 = float(dados.get('nota_1', 0.0))
        nota_2 = float(dados.get('nota_2', 0.0))
        faltas = int(dados.get('faltas', 0))

        novo_aluno.adicionar_nota(nota_1)
        novo_aluno.adicionar_nota(nota_2)
        novo_aluno.registrar_faltas(faltas)

        # 2. Prepara os dados exatamente com as colunas do CSV
        aluno_para_salvar = {
            "matricula": novo_aluno.matricula,
            "nome": novo_aluno.nome,
            "nota_1": nota_1,
            "nota_2": nota_2,
            "faltas": novo_aluno.faltas
        }

        # 3. Carrega o banco de dados atual com Pandas
        df_alunos = pd.read_csv(ARQUIVO_CSV)

        # 4. Transforma o novo aluno em uma mini-tabela do Pandas
        df_novo = pd.DataFrame([aluno_para_salvar])

        # 5. Junta a tabela antiga com o aluno novo
        df_atualizado = pd.concat([df_alunos, df_novo], ignore_index=True)

        # 6. SALVA DE VOLTA NO ARQUIVO CSV PARA SEMPRE
        df_atualizado.to_csv(ARQUIVO_CSV, index=False)

        logger.info(f"Aluno {novo_aluno.nome} salvo no disco com sucesso!")

        return jsonify({
            "mensagem": "Aluno cadastrado e salvo no CSV com sucesso!",
            "risco_evasao": novo_aluno.risco,
            "media_calculada": novo_aluno.calcular_media()
        }), 201

    except Exception as e:
        logger.error(f"Erro ao cadastrar: {e}")
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500


if __name__ == '__main__':
    logger.info("Iniciando o servidor do SIMPA na porta 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)
