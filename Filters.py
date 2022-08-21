import psycopg2
from datetime import datetime, date, timedelta
from statistics import mean


class Filter:

    def __init__(self, Connection):
        self.Connection = Connection

    def byAcesso(self, ID, Dias):
        Acessos = 0
        Cursor = self.Connection.cursor()
        Data = datetime.combine(date.today() - timedelta(days=Dias), datetime.min.time())
        Cursor.execute(f"SELECT * FROM tecnico WHERE id_cidade = '{ID}'")
        for Tecnicos in Cursor.fetchall():
            Cursor.execute(f"SELECT * FROM usuario WHERE id = '{Tecnicos[7]}'")
            Resultado = Cursor.fetchone()
            Comparacao = datetime.strptime(Resultado[2].strftime('%Y-%m-%d'), '%Y-%m-%d')
            if Comparacao >= Data:
                Acessos += 1
        Cursor.close()
        return Acessos

    def byAtendimento(self, ID, Dias):
        Atendimentos = 0
        Cursor = self.Connection.cursor()
        Data = datetime.combine(date.today() - timedelta(days=Dias), datetime.min.time())
        Cursor.execute(f"SELECT * FROM tecnico WHERE id_cidade = '{ID}'")
        Encontrados = Cursor.fetchall()
        if len(Encontrados) > 0:
            for Tecnico in Encontrados:
                Cursor.execute(f"SELECT * FROM atendimento WHERE id_tecnico = {Tecnico[0]}")
                for Tecnicos in Cursor.fetchall():
                    Visita = datetime.strptime(Tecnicos[2].strftime('%Y-%m-%d'), '%Y-%m-%d')
                    if Visita >= Data:
                        Atendimentos += 1
        Cursor.close()
        return Atendimentos

    def byNota(self, ID, Nota):
        Rendimento = 0
        Cursor = self.Connection.cursor()
        Cursor.execute(f"SELECT * FROM tecnico WHERE id_cidade = '{ID}'")
        Encontrados = tuple(map(lambda Identification: Identification[0], Cursor.fetchall()))
        if len(Encontrados) > 0:
            for Identification in Encontrados:
                Cursor.execute(f"SELECT * FROM atendimento WHERE id_tecnico = {Identification}")
                Notas = list(map(lambda _Nota: _Nota[4], Cursor.fetchall()))
                if len(Notas) > 0:
                    if mean(Notas) > Nota:
                        Rendimento += 1
        Cursor.close()
        return Rendimento
