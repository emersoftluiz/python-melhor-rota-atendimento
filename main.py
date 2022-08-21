from haversine import haversine, Unit
import psycopg2
from Map import Distance
from Filters import Filter
from flask import Flask, request
import json

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_AS_ASCII'] = False

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="root")

Max_Line_Distance = 20

@app.route("/estatistica")
def hello_world():
    Request = request.args.get('localizacao')
    if request.args.get('filtros') is not None:
        Filters = json.loads(request.args.get('filtros'))
    else:
        Filters = {}
    Retorno = []
    Data = []
    Cursor = conn.cursor()
    Filtros = Filter(conn)
    Cidade, Estado = getCidadeEstado(Request)
    Cursor.execute(f"SELECT * FROM cidade_brasil WHERE cidade = '{Cidade}' AND estado = '{Estado}'")
    Coordenadas = Cursor.fetchone()
    if Coordenadas is not None:
        Coordenadas = getCoordenadas(Coordenadas)
        Cursor.execute(f"SELECT * from cidade_brasil WHERE estado = '{Estado}'")
        for Consulta in Cursor.fetchall():
            Lugar = getCoordenadas(Consulta)
            Distancia = haversine((Coordenadas['Y'], Coordenadas['X']), (Lugar['Y'], Lugar['X']), unit=Unit.KILOMETERS)
            if Distancia <= Max_Line_Distance:
                Retorno.append(Consulta + (Distancia,))
        if len(Retorno) != 0:
            Retorno.sort(key=lambda x: x[len(x) - 1])
            Distancia = Distance(f"{Cidade}, {Estado}, Brazil", Max_Line_Distance)
            Distancia.setFrom(Coordenadas)
            for index in range(0, len(Retorno)):
                Distancia.setTo(getCoordenadas(Retorno[index]))
                Verificacao = Distancia.distance()
                if Verificacao <= Max_Line_Distance:
                    Resultado = {'cidade': Retorno[index][3],
                                 'estado': Retorno[index][1],
                                 'distancia': Verificacao}
                    if len(Filters) > 0:
                        for k, v in Filters.items():
                            if k == "Nota":
                                Resultado['tecnicos_nota_maior_que'] = Filtros.byNota(Retorno[index][0], v)
                            elif k == "Atendimento":
                                Resultado['tecnicos_atendimentos_ultimos_dias'] = Filtros.byAtendimento(
                                    Retorno[index][0],
                                    v)
                            elif k == "Acesso":
                                Resultado['tecnicos_acesso_sistema_ultimos_dias'] = Filtros.byAcesso(Retorno[index][0],
                                                                                                     v)
                    Data.append(Resultado)
                print(f"{index + 1}/{len(Retorno)}")
            return sorted(Data, key=lambda d: d['distancia'])
        else:
            return {"message": "Não foram encontradas cidades no raio exigido, por favor, reveja seus dados."}
    else:
        return {"message": "Dados invalidos, por favor, digite corretamente a cidade e estado. "
                           "Exemplo: 'Betim/Minas Gerais'"}


def getCidadeEstado(Request: str):
    return Request.split("/")


def getCoordenadas(Data: tuple):
    Coordenadas = list(map(float, reversed(Data[8].replace("(", "").replace(")", "")
                                           .split(","))))
    return {"X": Coordenadas[0], "Y": Coordenadas[1]}


if __name__ == "__main__":
    app.run()
