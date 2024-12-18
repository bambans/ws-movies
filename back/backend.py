from flask import Flask, request, jsonify
from flask_cors import CORS
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult

app = Flask(__name__)
CORS(app)

# Carregar a ontologia
graph = Graph()
graph.parse("ontologia.ttl", format="turtle")

@app.route("/query", methods=["POST"])
def query_graph():
    try:
        sparql_query = request.json.get("query", "")
        if not sparql_query:
            return jsonify({"error": "No query provided"}), 400

        # Executar a consulta SPARQL
        result = graph.query(sparql_query)
        response = format_result(result)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_result(result: SPARQLResult):
    """
    Formata o resultado da consulta SPARQL como uma lista de dicionários.
    """
    formatted_result = []
    for row in result:
        formatted_row = {str(var): str(row[var]) for var in result.vars}
        formatted_result.append(formatted_row)
    return {"results": formatted_result}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Servidor RDF ativo. Use o endpoint /query para consultas."})

@app.route('/movie', methods=['GET'])
def get_movie():
    """
    Endpoint para buscar informações de um filme ou listar todos os filmes.
    Query String: ?title=<título_do_filme>
    """
    movie_title = request.args.get('title')
    if movie_title:
        # Consulta SPARQL para buscar dados do filme específico
        sparql_query = f"""
        SELECT ?property ?value WHERE {{
            ?movie :temTítuloOriginal "{movie_title}" .
            ?movie ?property ?value .
        }}
        """

        result = graph.query(sparql_query)
        response = format_result(result)
        if not response:
            return jsonify({"error": f"Filme '{movie_title}' não encontrado."}), 404

        return jsonify(response)

    else:
        # Consulta SPARQL para listar todos os filmes
        sparql_query = f"""
        SELECT ?property ?value WHERE {{
            ?movie rdf:type ?class .
            ?class rdfs:subClassOf :Filme .
            ?movie ?property ?value .
        }}
        """

        result = graph.query(sparql_query)
        response = format_result(result)
        return jsonify(response)

@app.route('/actor', methods=['GET'])
def get_actor():
    """
    Endpoint para buscar dados de um ator pelo nome.
    Query String: ?name=<nome_do_ator>
    """
    actor_name = request.args.get('name')
    if actor_name:
    # Consulta SPARQL para buscar dados de um ator e os filmes relacionados
        sparql_query = f"""
        SELECT ?property ?value ?movie WHERE {{
            ?actor :temNomeAtor "{actor_name}" .
            ?actor ?property ?value .
            OPTIONAL {{ ?movie :temAtor ?actor . }}
        }}
        """
        result = graph.query(sparql_query)
        response = format_result(result)
        return jsonify(response)
    else:
        sparql_query = f"""
        SELECT ?property ?value ?movie WHERE {{
            ?actor rdf:type :Ator .
            ?actor ?property ?value .
            OPTIONAL {{ ?movie :temAtor ?actor . }}
        }}
        """
        result = graph.query(sparql_query)
        response = format_result(result)
        return jsonify(response)

@app.route('/director', methods=['GET'])
def get_director():
    """
    Endpoint para buscar dados de um diretor pelo nome.
    Query String: ?name=<nome_do_diretor>
    """
    director_name = request.args.get('name')
    if director_name:
        # Consulta SPARQL para buscar dados de um diretor e os filmes relacionados
        query = f"""
        SELECT ?property ?value ?movie WHERE {{
            ?director rdf:type :Diretor .
            ?director :temNomeDiretor "{director_name}" .
            ?director ?property ?value .
            OPTIONAL {{ ?movie :temDiretor ?director . }}
        }}
        """
        result = graph.query(query)
        response = format_result(result)
        return jsonify(response)
    else:
        sparql_query = f"""
        SELECT ?property ?value WHERE {{
            ?director rdf:type :Diretor .
            ?director ?property ?value .
        }}
        """
        result = graph.query(sparql_query)
        response = format_result(result)
        return jsonify(response)

@app.route('/user', methods=['GET'])
def get_user():
    """
    Endpoint para buscar dados de um usário pelo nome.
    Query String: ?name=<nome_do_usuário>
    """
    user_name = request.args.get('name')
    if user_name:
        # Consulta SPARQL para buscar dados de um usuário
        query = f"""
        SELECT ?property ?value WHERE {{
            ?user rdf:type :Usuário .
            ?user :temNomeUsuário "{user_name}" .
            ?user ?property ?value .
        }}
        """
        result = graph.query(query)
        response = format_result(result)
        return jsonify(response)
    else:
        query = f"""
        SELECT ?property ?value WHERE {{
            ?user rdf:type :Usuário .
            ?user ?property ?value .
        }}
        """
        result = graph.query(query)
        response = format_result(result)
        return jsonify(response)

@app.route('/rating', methods=['GET'])
def get_rating():
    """
    Endpoint para buscar dados de um usário pelo nome.
    Query String: ?name=<nome_do_usuário>
    """
    rating_user_name = request.args.get('name')
    if rating_user_name:
        # Consulta SPARQL para buscar dados de um usuário
        query = f"""
        SELECT ?property ?value WHERE {{
            ?rating rdf:type :Avaliação .
            ?rating :avaliadoPorUsuario ?user .
            ?user :temNomeUsuário "{rating_user_name}" .
            ?rating ?property ?value .
        }}
        """
        result = graph.query(query)
        response = format_result(result)
        return jsonify(response)
    else:
        query = f"""
        SELECT ?property ?value WHERE {{
            ?rating rdf:type :Avaliação .
            ?rating ?property ?value .
        }}
        """
        result = graph.query(query)
        response = format_result(result)
        return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
