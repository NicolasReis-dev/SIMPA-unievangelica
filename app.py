# Arquivo: app.py

from models.aluno import Aluno
from flask import Flask, jsonify, request
import matplotlib.pyplot as plt
import os
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')


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


@app.route('/dashboard', methods=['GET'])
def dashboard_estatistico():
    """Gera indicadores estatísticos avançados para a coordenação."""
    logger.info("Solicitação GET /dashboard recebida.")

    try:
        # 1. Carrega os dados com Pandas
        df_alunos = pd.read_csv(ARQUIVO_CSV)

        # 2. Calcula a média de CADA aluno e cria uma coluna virtual nova
        df_alunos['media_final'] = (
            df_alunos['nota_1'] + df_alunos['nota_2']) / 2

        # 3. Matemática Estatística Avançada do Marco 2
        estatisticas = {
            "01_total_alunos": int(len(df_alunos)),
            "02_media_geral_turma": round(float(df_alunos['media_final'].mean()), 2),
            "03_variancia_notas": round(float(df_alunos['media_final'].var()), 2),
            "04_desvio_padrao_notas": round(float(df_alunos['media_final'].std()), 2),
            "05_total_faltas_acumuladas": int(df_alunos['faltas'].sum()),
            "06_maior_nota_registrada": float(df_alunos['media_final'].max()),
            "07_menor_nota_registrada": float(df_alunos['media_final'].min())
        }

        # 4. Encontra os alunos "Gênios" e os em "Risco Extremo" usando filtros do Pandas
        melhor_aluno = df_alunos.loc[df_alunos['media_final'].idxmax()]

        # Filtra alunos com faltas > 10 e média < 5.0
        alunos_risco = df_alunos[(df_alunos['faltas'] > 10) & (
            df_alunos['media_final'] < 5.0)]

        resposta_completa = {
            "indicadores_globais": estatisticas,
            "insights_inteligentes": {
                "aluno_destaque": melhor_aluno['nome'],
                "quantidade_alunos_risco_critico": int(len(alunos_risco))
            }
        }

        return jsonify(resposta_completa), 200

    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return jsonify({"erro": f"Falha ao processar estatísticas: {str(e)}"}), 500


@app.route('/predicao', methods=['GET'])
def analise_preditiva():
    """Gera uma Regressão Linear simples e salva o gráfico de dispersão."""
    logger.info("Solicitação GET /predicao recebida.")

    try:
        df_alunos = pd.read_csv(ARQUIVO_CSV)
        df_alunos['media_final'] = (
            df_alunos['nota_1'] + df_alunos['nota_2']) / 2

        # 1. MATEMÁTICA DO NÍVEL 2: Regressão Linear (Faltas vs Média)
        x = df_alunos['faltas']
        y = df_alunos['media_final']

        # O polyfit acha o "Coeficiente Angular" (o quanto a nota cai) e o "Intercepto"
        coeficiente, intercepto = np.polyfit(x, y, 1)

        # 2. DESENHANDO O GRÁFICO (Visualização)
        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, color='blue', alpha=0.6,
                    label='Alunos (Dados Reais)')

        # Desenhando a linha de tendência matemática
        linha_tendencia = coeficiente * x + intercepto
        plt.plot(x, linha_tendencia, color='red', linewidth=2,
                 label='Linha de Tendência Preditiva')

        plt.title(
            'Inteligência Analítica: Impacto das Faltas na Média Final', fontsize=14)
        plt.xlabel('Quantidade de Faltas', fontsize=12)
        plt.ylabel('Média Final do Aluno', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)

        # 3. SALVANDO A IMAGEM NA PASTA DO PROJETO
        caminho_grafico = os.path.join('data', 'grafico_predicao.png')
        plt.savefig(caminho_grafico, bbox_inches='tight')
        plt.close()  # Limpa a memória para não pesar o servidor

        # 4. TRADUZINDO A MATEMÁTICA PARA O COORDENADOR
        impacto_formatado = round(abs(coeficiente), 2)
        insight = f"Para cada 1 falta que o aluno tem, a regressão indica que sua nota cai em média {impacto_formatado} pontos."

        return jsonify({
            "mensagem": "Análise preditiva concluída e gráfico salvo no disco!",
            "estatistica_avancada": {
                "coeficiente_angular": round(coeficiente, 4),
                "insight_traduzido": insight,
                "local_do_grafico": caminho_grafico
            }
        }), 200

    except Exception as e:
        logger.error(f"Erro ao gerar predição: {e}")
        return jsonify({"erro": f"Falha na regressão linear: {str(e)}"}), 500


if __name__ == '__main__':
    logger.info("Iniciando o servidor do SIMPA na porta 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)
