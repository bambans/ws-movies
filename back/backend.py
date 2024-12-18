from flask import Flask, request, jsonify
from flask_cors import CORS
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult

app = Flask(__name__)
CORS(app)

# Carregar a ontologia
graph = Graph()
graph.parse("ontologia.ttl", format="turtle")


def format_query_results(results: SPARQLResult):
    """
    Formata o resultado da consulta SPARQL como uma lista de dicionários.
    """
    formatted_results = []
    for row in results:
        formatted_row = {str(var): str(row[var]) for var in results.vars}
        formatted_results.append(formatted_row)
    return {"results": formatted_results}


@app.route("/query", methods=["POST"])
def query_graph():
    try:
        sparql_query = request.json.get("query", "")
        if not sparql_query:
            return jsonify({"error": "No query provided"}), 400

        # Executar a consulta SPARQL
        results = graph.query(sparql_query)
        response = format_query_results(results)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {"message": "Servidor RDF ativo. Use o endpoint /query para consultas."}
    )


@app.route("/movie", methods=["GET"])
def get_movie():
    """
    Endpoint para buscar informações de um filme ou listar todos os filmes.
    Query String: ?title=<título_do_filme>
    """
    movie_title = request.args.get("title")
    if movie_title:
        # Consulta SPARQL para buscar dados do filme específico
        sparql_query = f"""
        SELECT ?movie_title ?property ?value WHERE {{
            ?movie :temTítuloOriginal "{movie_title}" .
            ?movie ?property ?value .
            ?movie :temTítuloOriginal ?movie_title .
        }}
        """
    else:
        # Consulta SPARQL para listar todos os filmes
        sparql_query = f"""
        SELECT ?movie_title ?property ?value WHERE {{
            ?movie rdf:type ?class .
            ?class rdfs:subClassOf :Filme .
            ?movie ?property ?value .
            ?movie :temTítuloOriginal ?movie_title .
        }}
        """
    
    results = graph.query(sparql_query)

    # Organizar os resultados em uma lista de filmes
    movies_dict = {}
    
    for result in results:
        movie_title = str(result.movie_title)

        if movie_title not in movies_dict:
            movies_dict[movie_title] = {}
        
        property_name = str(result.property).split("/")[-1]
        value = str(result.value).split("/")[-1]

        if property_name not in movies_dict[movie_title]:
            movies_dict[movie_title][property_name] = []
        movies_dict[movie_title][property_name].append(value)
    
    if not movies_dict:
        return jsonify({"error": f"Filme '{movie_title}' não encontrado."}), 404

    return jsonify(movies_dict)


@app.route("/actor", methods=["GET"])
def get_actor():
    """
    Endpoint para buscar dados de um ator pelo nome.
    Query String: ?name=<nome_do_ator>
    """
    actor_name = request.args.get("name")
    if actor_name:
        # Consulta SPARQL para buscar dados de um ator e os filmes relacionados
        sparql_query = f"""
        SELECT ?actor_name ?movie_title WHERE {{
            ?actor rdf:type :Ator .
            ?actor :temNomeAtor "{actor_name}" .
            ?actor :temNomeAtor ?actor_name .
            OPTIONAL {{ ?movie :temAtor ?actor .
                        ?movie :temTítuloOriginal ?movie_title . }}
        }}
        """
    else:
        sparql_query = f"""
        SELECT ?actor_name ?movie_title WHERE {{
            ?actor rdf:type :Ator .
            ?actor :temNomeAtor ?actor_name .
            OPTIONAL {{
                ?movie :temAtor ?actor .
                ?movie :temTítuloOriginal ?movie_title .
                }}
        }}
        """
    
    results = graph.query(sparql_query)

    # Organizar os resultados em um formato legível
    actor_dict = {}

    for result in results:
        actor_name = str(result.actor_name)

        if actor_name not in actor_dict:
            actor_dict[actor_name] = []
        
        actor_dict[actor_name].append(str(result.movie_title))
    
    if not actor_dict:
        return jsonify({"error": f"Ator '{actor_name}' não encontrado."}), 404

    return jsonify(actor_dict)


@app.route("/director", methods=["GET"])
def get_director():
    """
    Endpoint para buscar dados de um diretor pelo nome.
    Query String: ?name=<nome_do_diretor>
    """
    director_name = request.args.get("name")
    if director_name:
        # Consulta SPARQL para buscar dados de um diretor e os filmes relacionados
        sparql_query = f"""
        SELECT ?director_name ?movie_title WHERE {{
            ?director rdf:type :Diretor .
            ?director :temNomeDiretor "{director_name}" .
            ?director :temNomeDiretor ?director_name .
            OPTIONAL {{
                ?movie :temDiretor ?director .
                ?movie :temTítuloOriginal ?movie_title .
                }}
        }}
        """
    else:
        sparql_query = f"""
        SELECT ?director_name ?movie_title WHERE {{
            ?director rdf:type :Diretor .
            ?director :temNomeDiretor ?director_name .
            OPTIONAL {{
                ?movie :temDiretor ?director .
                ?movie :temTítuloOriginal ?movie_title .
                }}
        }}
        """
    
    results = graph.query(sparql_query)

    # Organizar os resultados em um formato legível
    director_dict = {}

    for result in results:
        director_name = str(result.director_name)

        if director_name not in director_dict:
            director_dict[director_name] = []
        
        director_dict[director_name].append(str(result.movie_title))
    
    if not director_dict:
        return jsonify({"error": f"Diretor '{director_name}' não encontrado."}), 404

    return jsonify(director_dict)


@app.route("/user", methods=["GET"])
def get_user():
    """
    Endpoint para buscar dados de um usário pelo nome.
    Query String: ?name=<nome_do_usuário>
    """
    user_name = request.args.get("name")
    if user_name:
        # Consulta SPARQL para buscar dados de um usuário
        sparql_query = f"""
        SELECT ?user_name ?property ?value WHERE {{
            ?user rdf:type :Usuário .
            ?user :temNomeUsuário "{user_name}" .
            ?user :temNomeUsuário ?user_name .
            ?user ?property ?value .
        }}
        """
    else:
        sparql_query = f"""
        SELECT ?user_name ?property ?value WHERE {{
            ?user rdf:type :Usuário .
            ?user :temNomeUsuário ?user_name .
            ?user ?property ?value .
        }}
        """
    
    results = graph.query(sparql_query)
    
    user_dict = {}
    
    for result in results:
        user_name = str(result.user_name)

        if user_name not in user_dict:
            user_dict[user_name] = {}
        
        property_name = str(result.property).split("/")[-1]
        value = str(result.value).split("/")[-1]

        if property_name not in user_dict[user_name]:
            user_dict[user_name][property_name] = []
        
        user_dict[user_name][property_name].append(value)
    
    if not user_dict:
        return jsonify({"error": f"Usuário '{user_name}' não encontrado."}), 404

    return jsonify(user_dict)


@app.route("/rating_user", methods=["GET"])
def get_rating_user():
    """
    Endpoint para buscar dados de um usário pelo nome.
    Query String: ?name=<nome_do_usuário>
    """
    rating_user_name = request.args.get("name")
    if rating_user_name:
        # Consulta SPARQL para buscar dados de um usuário
        sparql_query = f"""
        SELECT ?user_name ?movie_title ?score WHERE {{
            ?rating rdf:type :Avaliação .
            ?rating :avaliadoPorUsuario ?user .
            ?user :temNomeUsuário "{rating_user_name}" .
            ?user :temNomeUsuário ?username .
            ?rating :avaliouFilme ?movie .
            ?movie :temTítuloOriginal ?movie_title .
            ?rating :temNota ?score .
        }}
        """
    else:
        sparql_query = f"""
        SELECT ?user_name ?movie_title ?score WHERE {{
            ?rating rdf:type :Avaliação .
            ?rating :avaliadoPorUsuario ?user .
            ?user :temNomeUsuário ?username .
            ?rating :avaliouFilme ?movie .
            ?movie :temTítuloOriginal ?movie_title .
            ?rating :temNota ?score .
        }}
        """
    results = graph.query(sparql_query)

    user_dict = {}
    
    for result in results:
        user_name = str(result.user_name)

        if user_name not in user_dict:
            user_dict[user_name] = {}
        
        movie_title = str(result.movie_title).split("/")[-1]
        score = str(result.score).split("/")[-1]

        if movie_title not in user_dict[user_name]:
            user_dict[user_name][movie_title] = []
        
        user_dict[user_name][movie_title].append(score)
    
    if not user_dict:
        return jsonify({"error": f"Usuário '{user_name}' não encontrado."}), 404

    return jsonify(user_dict)

if __name__ == "__main__":
    app.run(debug=True)
