# 🎓 SIMPA - Sistema Inteligente de Monitoramento e Predição Acadêmica

O SIMPA é uma plataforma analítica orientada a dados, desenvolvida como Projeto Integrador do 2º Período de Inteligência Artificial da UniEVANGÉLICA. 

O objetivo do sistema é analisar notas, frequência e indicadores acadêmicos para identificar padrões, estimar riscos de evasão e oferecer recomendações estratégicas para a coordenação.

## 🏗️ Arquitetura do Projeto (Ciclo 1)
O projeto segue a estrutura recomendada de separação de responsabilidades:
* `models/`: Entidades centrais e regras de negócio usando Programação Orientada a Objetos (POO).
* `api/`: Rotas Flask/FastAPI para comunicação web.
* `services/`: Cálculos estatísticos e validações de risco.
* `data/`: Base de dados simulada (CSV/JSON).
* `docs/`: Documentação e Diagramas UML.

## 📊 Dicionário de Dados (`alunos.csv`)
* `matricula`: (Texto) Código de identificação único do aluno. Espera-se 7 dígitos.
* `nome`: (Texto) Nome completo ou primeiro nome do aluno.
* `nota_1`: (Decimal) Nota da primeira avaliação. Valores esperados entre 0.0 e 10.0.
* `nota_2`: (Decimal) Nota da segunda avaliação. Valores esperados entre 0.0 e 10.0.
* `faltas`: (Inteiro) Número total de aulas que o aluno faltou. Valores esperados de 0 para cima.

## 📐 Modelagem Documentada (UML)
Abaixo estão os diagramas estruturais do sistema para o Marco 1, detalhando a arquitetura Orientada a Objetos e os Casos de Uso da API.

### Diagrama de Classes
```mermaid
classDiagram
    class Aluno {
        -String matricula
        -String nome
        -list notas
        -int faltas
        -bool status_risco
        +adicionar_nota(nota) void
        +registrar_faltas(quantidade) void
        +calcular_media() float
        -atualizar_risco() void
    }
```

### Diagrama de Casos de Uso (API)
```mermaid
flowchart LR
    A[Usuário da API / Coordenador] --> B(Cadastrar Aluno via POST)
    A --> C(Consultar Lista de Alunos via GET)
    A --> D(Verificar Status de Risco)
    
    D -. "usa internamente" .-> E(Cálculo Automático de Média e Faltas)
```

## 🚀 Tecnologias Utilizadas
* Python 3
* Flask (Criação da API)
* Pandas / Numpy (Para análise de dados futura)

## ⚙️ Como Executar o Projeto

Siga os passos abaixo para rodar a API localmente na sua máquina:

1. **Clone o repositório ou extraia o arquivo ZIP.**
2. **Abra o terminal e navegue até a pasta raiz do projeto:**
   ```bash
   cd simpa-unievangelica
   ```
3. **Instale as dependências necessárias:**
   O projeto utiliza o Flask. Para instalar, rode o comando:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ou instale manualmente usando `pip install flask`)*
4. **Inicie o servidor da API:**
   ```bash
   python app.py
   ```
5. **Acesse no Navegador ou via Postman/Insomnia:**
   A API estará rodando no endereço: `http://localhost:5001/`
   * Para ver o status: Acesse `GET http://localhost:5001/`
   * Para listar os alunos: Acesse `GET http://localhost:5001/alunos`

## 👥 Equipe de Desenvolvimento
1. Nicolas Reis
2. Paula Tomazzelli
3. Tales Ferreira
4. Enzo Garcia
5. Joao Pedro Silva Reis
6. João Gabriel Neres Araújo
7. Matheus Felipe