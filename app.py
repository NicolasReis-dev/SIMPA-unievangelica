import logging
from flask import Flask, jsonify

# -------------------------------------------------------------------------
# 1. SETUP DO VAR (Configuração do Log Verboso)
# -------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG, # Nível fofoqueiro máximo ativado
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger("SIMPA_API")

# -------------------------------------------------------------------------
# 2. INICIALIZAÇÃO DO FLASK (A nossa API)
# -------------------------------------------------------------------------
app = Flask(__name__)

# Dados simulados provisórios (A Tarefa 5 do Trello vai trocar isso depois pelo CSV real)
alunos_simulados = [
    {"matricula": "2026001", "nome": "Nicolas", "risco": False},
    {"matricula": "2026002", "nome": "Carlos", "risco": True}
]

# -------------------------------------------------------------------------
# 3. ROTAS DA API (Os "Caminhos" de comunicação)
# -------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    """Rota raiz para testar se o servidor está online."""
    logger.info("Acessaram a rota principal (Raiz).")
    return jsonify({
        "sistema": "SIMPA - UniEVANGÉLICA",
        "status": "Online e operando",
        "versao": "1.0 - Ciclo 1"
    })

@app.route('/alunos', methods=['GET'])
def listar_alunos():
    """Rota que devolve a lista de alunos (Exigência do Marco 1)."""
    logger.info("Solicitação para listar todos os alunos recebida.")
    logger.debug(f"Enviando {len(alunos_simulados)} alunos para o cliente.")
    
    # Retorna os dados formatados em JSON [cite: 342]
    return jsonify({
        "total_alunos": len(alunos_simulados),
        "alunos": alunos_simulados
    })

# -------------------------------------------------------------------------
# 4. RODANDO O SERVIDOR
# -------------------------------------------------------------------------
if __name__ == '__main__':
    logger.info("Iniciando o servidor do SIMPA na porta 5001...")
    # debug=True reinicia o servidor sozinho se você alterar o código depois
    app.run(debug=True, host='0.0.0.0', port=5001)