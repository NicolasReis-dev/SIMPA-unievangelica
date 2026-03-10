from flask import Flask, jsonify, request
import pandas as pd
import os

app = Flask(__name__)
CSV_PATH = 'data/alunos.csv'
@app.route('/')
def index():
    return '<h1>SIMPA - API Rodando!</h1><p><a href="/alunos">Ver alunos</a></p>'

@app.route('/alunos', methods=['GET'])
def listar_alunos():
    df = pd.read_csv(CSV_PATH)
    return jsonify(df.to_dict(orient='records'))


@app.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    dados = request.get_json()

    # Valida campos obrigatórios
    campos_obrigatorios = ['matricula', 'nome', 'nota_1', 'nota_2', 'faltas']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400

    # Lê o CSV atual
    df = pd.read_csv(CSV_PATH)

    # Verifica matrícula duplicada
    if str(dados['matricula']) in df['matricula'].astype(str).values:
        return jsonify({'erro': 'Matrícula já cadastrada'}), 409

    # Monta o novo aluno
    novo_aluno = {
        'matricula': str(dados['matricula']),
        'nome': str(dados['nome']),
        'nota_1': float(dados['nota_1']),
        'nota_2': float(dados['nota_2']),
        'faltas': int(dados['faltas'])
    }

    # Adiciona ao DataFrame e salva no CSV
    novo_df = pd.concat([df, pd.DataFrame([novo_aluno])], ignore_index=True)
    novo_df.to_csv(CSV_PATH, index=False)

    return jsonify({'mensagem': 'Aluno cadastrado com sucesso!', 'aluno': novo_aluno}), 201


if __name__ == '__main__':
    app.run(debug=True)