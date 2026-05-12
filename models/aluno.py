# Arquivo: models/aluno.py

class Usuario:
    """Classe Mãe (Superclasse) - Aplicação de Herança"""

    def __init__(self, matricula, nome):
        # Atributos protegidos (um underline) para as classes filhas poderem acessar
        self._matricula = matricula
        self._nome = nome

    @property
    def matricula(self): return self._matricula

    @property
    def nome(self): return self._nome

    def painel_de_acesso(self):
        """Método genérico que será sobrescrito (Polimorfismo)"""
        return f"Acesso padrão para o usuário: {self._nome}"


class Aluno(Usuario):
    """Classe Filha que herda de Usuario"""

    def __init__(self, matricula, nome):
        super().__init__(matricula, nome)  # Chama o construtor da classe mãe
        self.__notas = []
        self.__faltas = 0
        self.__status_risco = False

    @property
    def faltas(self):
        return self.__faltas

    @property
    def risco(self):
        return self.__status_risco

    # Regras de Negócio Específicas do Aluno
    def adicionar_nota(self, nota):
        self.__notas.append(nota)
        self.__atualizar_risco()

    def registrar_faltas(self, quantidade):
        self.__faltas += quantidade
        self.__atualizar_risco()

    def calcular_media(self):
        if not self.__notas: return 0.0
        return sum(self.__notas) / len(self.__notas)

    def __atualizar_risco(self):
        if self.calcular_media() < 6.0 or self.__faltas > 10:
            self.__status_risco = True
        else:
            self.__status_risco = False

    # POLIMORFISMO: Sobrescrevendo o método da classe mãe
    def painel_de_acesso(self):
        status = 'ALTO RISCO' if self.risco else 'Regular'
        return f"Painel do Aluno | Nome: {self.nome} | Status: {status}"


class Coordenador(Usuario):
    """Outra Classe Filha que herda de Usuario"""

    def __init__(self, matricula, nome, departamento):
        super().__init__(matricula, nome)
        self.departamento = departamento

    # POLIMORFISMO: Sobrescrevendo o método da classe mãe
    def painel_de_acesso(self):
        return f"Painel da Coordenação | Prof. {self.nome} | Depto: {self.departamento} | ACESSO TOTAL LIBERADO"