# Arquivo: models/aluno.py

class Aluno:
    """Classe que representa a entidade Aluno com encapsulamento."""

    def __init__(self, matricula, nome):
        self.__matricula = matricula
        self.__nome = nome
        self.__notas = []
        self.__faltas = 0
        self.__status_risco = False

    # Getters
    @property
    def matricula(self):
        return self.__matricula

    @property
    def nome(self):
        return self.__nome

    @property
    def faltas(self):
        return self.__faltas

    @property
    def risco(self):
        return self.__status_risco

    # Regras de Negócio
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
        """Lógica interna: Risco se a média for menor que 6.0 ou faltas > 10"""
        if self.calcular_media() < 6.0 or self.__faltas > 10:
            self.__status_risco = True
        else:
            self.__status_risco = False