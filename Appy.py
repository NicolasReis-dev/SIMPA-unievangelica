# Arquivo: Appy.py

from groq import Groq
from models.aluno import Aluno
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import os
from dotenv import load_dotenv
import logging
import pandas as pd
import numpy as np
import json
import sqlite3
from datetime import datetime
from functools import wraps

load_dotenv()
chave_API = os.getenv("GROQ_API_KEY")
SENHA_SISTEMA = os.getenv("SIMPA_SENHA", "simpa2026")  # Senha padrão, altere no .env
client = Groq(api_key=chave_API)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger("SIMPA_API")

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
app.secret_key = os.getenv("SIMPA_SECRET", "simpa-secret-key-2026")

DB_PATH = os.path.join('data', 'simpa.db')
ARQUIVO_HISTORICO = os.path.join('data', 'historico_ia.json')
ARQUIVO_CSV = os.path.join('data', 'alunos.csv')  # mantido para migração


# ─── BANCO DE DADOS ────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas e migra dados do CSV se o banco estiver vazio."""
    os.makedirs('data', exist_ok=True)
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            matricula   INTEGER PRIMARY KEY,
            nome        TEXT NOT NULL,
            nota_1      REAL DEFAULT 0.0,
            nota_2      REAL DEFAULT 0.0,
            faltas      INTEGER DEFAULT 0,
            criado_em   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Migra CSV → SQLite se o banco estiver vazio
    count = conn.execute('SELECT COUNT(*) FROM alunos').fetchone()[0]
    if count == 0 and os.path.exists(ARQUIVO_CSV):
        try:
            df = pd.read_csv(ARQUIVO_CSV)
            for _, row in df.iterrows():
                conn.execute(
                    'INSERT OR IGNORE INTO alunos (matricula, nome, nota_1, nota_2, faltas) VALUES (?,?,?,?,?)',
                    (int(row['matricula']), row['nome'], float(row['nota_1']), float(row['nota_2']), int(row['faltas']))
                )
            conn.commit()
            logger.info(f"Migração CSV → SQLite concluída: {len(df)} alunos importados.")
        except Exception as e:
            logger.error(f"Erro na migração: {e}")
    conn.close()


# ─── AUTH ──────────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logado'):
            return jsonify({"erro": "Não autorizado. Faça login."}), 401
        return f(*args, **kwargs)
    return decorated


# ─── HISTÓRICO IA ──────────────────────────────────────────────────────────────

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def salvar_historico(historico):
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


# ─── ROTAS DE AUTH ─────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET'])
def login():
    if session.get('logado'):
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def fazer_login():
    dados = request.get_json()
    if dados and dados.get('senha') == SENHA_SISTEMA:
        session['logado'] = True
        session.permanent = True
        logger.info("Login realizado com sucesso.")
        return jsonify({"sucesso": True}), 200
    logger.warning("Tentativa de login com senha incorreta.")
    return jsonify({"erro": "Senha incorreta."}), 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── ROTAS DE PÁGINAS ──────────────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    logger.info("Acessaram o site principal.")
    return render_template('index.html')


@app.route('/pagina_alunos')
@login_required
def pagina_alunos():
    return render_template('alunos.html')


@app.route('/relatorio/<int:matricula>')
@login_required
def pagina_relatorio(matricula):
    return render_template('relatorio.html', matricula=matricula)


@app.route('/configuracoes')
@login_required
def pagina_configuracoes():
    return render_template('configuracoes.html')


@app.route('/analise')
@login_required
def pagina_analise():
    return render_template('analise.html')


# ─── API: ALUNOS ───────────────────────────────────────────────────────────────

@app.route('/alunos', methods=['GET'])
@api_login_required
def listar_alunos():
    logger.info("Solicitação GET /alunos recebida.")
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM alunos ORDER BY nome').fetchall()
        conn.close()
        alunos = []
        for r in rows:
            a = dict(r)
            a['media_atual'] = round((a['nota_1'] + a['nota_2']) / 2, 2)
            alunos.append(a)
        return jsonify({"total_alunos": len(alunos), "alunos": alunos}), 200
    except Exception as e:
        logger.error(f"Erro ao listar alunos: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route('/alunos/<int:matricula>', methods=['GET'])
@api_login_required
def buscar_aluno(matricula):
    try:
        conn = get_db()
        row = conn.execute('SELECT * FROM alunos WHERE matricula=?', (matricula,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"erro": "Aluno não encontrado."}), 404
        a = dict(row)
        a['media_atual'] = round((a['nota_1'] + a['nota_2']) / 2, 2)
        media = a['media_atual']
        faltas = a['faltas']
        if media >= 7 and faltas <= 5:    prob = 95
        elif media >= 6:                  prob = 75
        elif media >= 5:                  prob = 50
        elif media >= 4:                  prob = 25
        else:                             prob = 10
        if faltas > 15:   prob = max(5, prob - 30)
        elif faltas > 10: prob = max(5, prob - 15)
        a['prob_aprovacao'] = prob
        a['historico_orientacoes'] = [h for h in carregar_historico() if h.get('tipo') == 'individual' and h.get('matricula') == matricula]
        return jsonify(a), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/alunos', methods=['POST'])
@api_login_required
def cadastrar_aluno():
    dados = request.get_json()
    if not dados or 'matricula' not in dados or 'nome' not in dados:
        return jsonify({"erro": "Dados incompletos."}), 400
    try:
        novo_aluno = Aluno(matricula=dados['matricula'], nome=dados['nome'])
        nota_1 = float(dados.get('nota_1', 0.0))
        nota_2 = float(dados.get('nota_2', 0.0))
        faltas = int(dados.get('faltas', 0))
        novo_aluno.adicionar_nota(nota_1)
        novo_aluno.adicionar_nota(nota_2)
        novo_aluno.registrar_faltas(faltas)
        conn = get_db()
        conn.execute(
            'INSERT OR REPLACE INTO alunos (matricula, nome, nota_1, nota_2, faltas) VALUES (?,?,?,?,?)',
            (int(dados['matricula']), dados['nome'], nota_1, nota_2, faltas)
        )
        conn.commit()
        conn.close()
        logger.info(f"Aluno {dados['nome']} salvo no banco.")
        return jsonify({
            "mensagem": "Aluno cadastrado com sucesso!",
            "risco_evasao": novo_aluno.risco,
            "media_calculada": novo_aluno.calcular_media()
        }), 201
    except Exception as e:
        logger.error(f"Erro ao cadastrar: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route('/alunos/<int:matricula>', methods=['DELETE'])
@api_login_required
def deletar_aluno(matricula):
    try:
        conn = get_db()
        conn.execute('DELETE FROM alunos WHERE matricula=?', (matricula,))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Aluno removido com sucesso."}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── API: DASHBOARD ────────────────────────────────────────────────────────────

@app.route('/dashboard', methods=['GET'])
@api_login_required
def dashboard_estatistico():
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM alunos').fetchall()
        conn.close()
        if not rows:
            return jsonify({"erro": "Nenhum aluno cadastrado."}), 404
        df = pd.DataFrame([dict(r) for r in rows])
        df['media_final'] = (df['nota_1'] + df['nota_2']) / 2
        melhor = df.loc[df['media_final'].idxmax()]
        risco  = df[(df['faltas'] > 10) & (df['media_final'] < 5.0)]
        return jsonify({
            "indicadores_globais": {
                "01_total_alunos": int(len(df)),
                "02_media_geral_turma": round(float(df['media_final'].mean()), 2),
                "03_variancia_notas": round(float(df['media_final'].var()), 2),
                "04_desvio_padrao_notas": round(float(df['media_final'].std()), 2),
                "05_total_faltas_acumuladas": int(df['faltas'].sum()),
                "06_maior_nota_registrada": float(df['media_final'].max()),
                "07_menor_nota_registrada": float(df['media_final'].min())
            },
            "insights_inteligentes": {
                "aluno_destaque": melhor['nome'],
                "quantidade_alunos_risco_critico": int(len(risco))
            }
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── API: PREDIÇÃO ─────────────────────────────────────────────────────────────

@app.route('/predicao', methods=['GET'])
@api_login_required
def analise_preditiva():
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM alunos').fetchall()
        conn.close()
        df = pd.DataFrame([dict(r) for r in rows])
        df['media_final'] = (df['nota_1'] + df['nota_2']) / 2
        x = df['faltas'].tolist()
        y = df['media_final'].tolist()
        coef, intercept = np.polyfit(x, y, 1)
        insight = f"Para cada 1 falta que o aluno tem, a regressão indica que sua nota cai em média {round(abs(coef), 2)} pontos."
        return jsonify({
            "dados_grafico": {"nomes": df['nome'].tolist(), "faltas": x, "medias": y},
            "estatistica_avancada": {
                "coeficiente_angular": round(coef, 4),
                "intercepto": round(intercept, 4),
                "insight_traduzido": insight,
                "media_nota1": round(float(df['nota_1'].mean()), 2),
                "media_nota2": round(float(df['nota_2'].mean()), 2),
                "variancia": round(float(df['media_final'].var()), 2),
            }
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── API: HEATMAP ──────────────────────────────────────────────────────────────

@app.route('/heatmap', methods=['GET'])
@api_login_required
def gerar_heatmap():
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM alunos').fetchall()
        conn.close()
        resultado = []
        for r in rows:
            a = dict(r)
            m = round((a['nota_1'] + a['nota_2']) / 2, 2)
            f = a['faltas']
            if f > 10 and m < 5:   nivel = 3
            elif f > 8 or m < 6:   nivel = 2
            elif f > 5 or m < 7:   nivel = 1
            else:                  nivel = 0
            resultado.append({**a, 'media': m, 'nivel': nivel})
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── API: IA ───────────────────────────────────────────────────────────────────

@app.route('/orientacao_ia', methods=['GET'])
@api_login_required
def gerar_orientacao_ia():
    try:
        conn = get_db()
        rows = conn.execute('SELECT * FROM alunos').fetchall()
        conn.close()
        df = pd.DataFrame([dict(r) for r in rows])
        df['media_final'] = (df['nota_1'] + df['nota_2']) / 2
        risco = df[(df['faltas'] > 10) & (df['media_final'] < 5.0)]
        if risco.empty:
            return jsonify({"mensagem": "Ótima notícia! Nenhum aluno em risco crítico no momento."}), 200
        lista = "".join([f"- {r['nome']} | Média: {r['media_final']:.2f} | Faltas: {r['faltas']}\n" for _, r in risco.iterrows()])
        prompt = f"Aja como Coordenador Pedagógico sênior. Alunos em risco:\n{lista}\nGere plano de ação em 2 parágrafos. Português do Brasil."
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=500)
        texto = resp.choices[0].message.content
        h = carregar_historico()
        h.insert(0, {"tipo": "turma", "data": datetime.now().strftime("%d/%m/%Y %H:%M"), "alunos_analisados": len(risco), "texto": texto})
        salvar_historico(h[:20])
        return jsonify({"status": "sucesso", "alunos_analisados": len(risco), "orientacao_pedagogica_ia": texto}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/orientacao_individual', methods=['POST'])
@api_login_required
def gerar_orientacao_individual():
    dados = request.get_json()
    if not dados or 'matricula' not in dados:
        return jsonify({"erro": "Matrícula não informada."}), 400
    try:
        conn = get_db()
        row = conn.execute('SELECT * FROM alunos WHERE matricula=?', (int(dados['matricula']),)).fetchone()
        conn.close()
        if not row:
            return jsonify({"erro": "Aluno não encontrado."}), 404
        a = dict(row)
        media = round((a['nota_1'] + a['nota_2']) / 2, 2)
        prompt = f"Coordenador Pedagógico sênior. Aluno: {a['nome']} | N1:{a['nota_1']} N2:{a['nota_2']} Média:{media} Faltas:{a['faltas']}. Orientação personalizada em 2 parágrafos. Português do Brasil."
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=400)
        texto = resp.choices[0].message.content
        h = carregar_historico()
        h.insert(0, {"tipo": "individual", "data": datetime.now().strftime("%d/%m/%Y %H:%M"), "aluno": a['nome'], "matricula": int(a['matricula']), "media": media, "faltas": a['faltas'], "texto": texto})
        salvar_historico(h[:20])
        return jsonify({"status": "sucesso", "aluno": a['nome'], "orientacao": texto}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/gerar_email', methods=['POST'])
@api_login_required
def gerar_email():
    dados = request.get_json()
    if not dados or 'matricula' not in dados:
        return jsonify({"erro": "Matrícula não informada."}), 400
    try:
        conn = get_db()
        row = conn.execute('SELECT * FROM alunos WHERE matricula=?', (int(dados['matricula']),)).fetchone()
        conn.close()
        if not row:
            return jsonify({"erro": "Aluno não encontrado."}), 404
        a = dict(row)
        media = round((a['nota_1'] + a['nota_2']) / 2, 2)
        prompt = f"Coordenador pedagógico. E-mail formal e empático para {a['nome']} (média {media}, {a['faltas']} faltas). Assunto na 1ª linha. Máx 3 parágrafos. Português do Brasil."
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=400)
        return jsonify({"status": "sucesso", "aluno": a['nome'], "email": resp.choices[0].message.content}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/historico_ia', methods=['GET'])
@api_login_required
def historico_ia():
    return jsonify(carregar_historico()), 200


# ─── INIT ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    logger.info("Iniciando o servidor do SIMPA na porta 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)