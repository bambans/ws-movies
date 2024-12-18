from flask import Flask, request, jsonify
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF
from flask_cors import CORS
from rdflib.plugins.sparql.processor import SPARQLResult

app = Flask(__name__)
CORS(app)

# Carregar a ontologia
graph = Graph()
graph.parse("ontologia.ttl", format="turtle")

# Namespaces
ns = Namespace("http://www.amazingvideo.com/ontology#")
graph.bind("amazing", ns)

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

@app.route("/register", methods=["POST"])
def register_user():
    """
    Endpoint para registrar um novo usuário.
    Body JSON: { "name": "<nome_do_usuário>", "email": "<email_do_usuário>", "password": "<senha_do_usuário>" }
    """
    user_data = request.get_json()
    user_name = user_data.get("name")
    user_email = user_data.get("email")
    user_number = user_data.get("number")

    if not user_name or not user_email or not user_number:
        return jsonify({"error": "Nome, email e número são obrigatórios."}), 400

    # Consulta SPARQL para inserir um novo usuário
    sparql_insert = f"""
    INSERT DATA {{
        :{user_name.replace(" ", "_")} rdf:type :Usuário ;
                    :temNomeUsuário "{user_name}" ;
                    :temEmail "{user_email}" ;
                    :temWhatsapp "{user_number}" .
    }}
    """

    try:
        graph.update(sparql_insert)
        return jsonify({"message": "Usuário registrado com sucesso."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_rating", methods=["POST"])
def add_rating():
    try:
        data = request.json
        user_name = data.get("user")
        movie_title = data.get("movie")
        rating = data.get("rating")

        if not (user_name and movie_title and rating):
            return jsonify({"error": "Missing user, movie, or rating."}), 400

        # Buscar ou criar recursos
        user = URIRef(f"{ns}{user_name.replace(' ', '_')}")
        movie = URIRef(f"{ns}{movie_title.replace(' ', '_')}")
        rating_instance = URIRef(f"{ns}rating_{user_name.replace(' ', '_')}_{movie_title.replace(' ', '_')}")

        # Adicionar ao grafo
        graph.add((rating_instance, RDF.type, ns.Avaliacao))
        graph.add((rating_instance, ns.avaliadoPorUsuario, user))
        graph.add((rating_instance, ns.avaliouFilme, movie))
        graph.add((rating_instance, ns.temNota, Literal(rating)))

        return jsonify({"message": "Rating added successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_preference", methods=["POST"])
def add_preference():
    try:
        data = request.json
        user_name = data.get("user")
        preference = data.get("preference")

        if not (user_name and preference):
            return jsonify({"error": "Missing user or preference."}), 400

        # Buscar ou criar recursos
        user = URIRef(f"{ns}{user_name.replace(' ', '_')}")
        thematic = URIRef(f"{ns}{preference.replace(' ', '_')}")

        # Adicionar ao grafo
        graph.add((user, ns.temPreferencia, thematic))

        return jsonify({"message": "Preference added successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

@app.route("/user/preferences", methods=["GET"])
def get_user_preferences():
    """
    Endpoint para buscar dados de um usário pelo nome.
    Query String: ?name=<nome_do_usuário>
    """
    user_name = request.args.get("name")
    if user_name:
        # Consulta SPARQL para buscar dados de um usuário
        sparql_query = f"""
        SELECT ?user_name ?preference WHERE {{
            ?user rdf:type :Usuário .
            ?user :temNomeUsuário "{user_name}" .
            ?user :temNomeUsuário ?user_name .
            ?user :temPreferência ?preference .
        }}
        """
    else:
        sparql_query = f"""
        SELECT ?user_name ?preference WHERE {{
            ?user rdf:type :Usuário .
            ?user :temNomeUsuário ?user_name .
            ?user :temPreferência ?preference .
        }}
        """

    result = graph.query(sparql_query)
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

@app.route("/recommendations", methods=["GET"])
def recommend_movies():
    """
    Endpoint para recomendar filmes com base nas preferências do usuário.
    Query String: ?name=<nome_do_usuário>
    """
    user_name = request.args.get("name")
    if not user_name:
        return jsonify({"error": "Nome do usuário é obrigatório."}), 400

    # Consulta SPARQL para recomendar filmes com base nas preferências do usuário
    sparql_query = f"""
    SELECT ?movie_title WHERE {{
        ?user rdf:type :Usuário ;
              :temNomeUsuário "{user_name}" ;
              :temPreferência ?preference .
        ?class rdfs:subClassOf :Filme .
        ?movie rdf:type ?class ;
               :temGênero ?preference ;
               :temTítuloOriginal ?movie_title .
        ?movie rdf:type ?class ;
            :temAtor ?preference ;
            :temTítuloOriginal ?movie_title .
        FILTER NOT EXISTS {{
            ?rating rdf:type :Avaliação ;
                    :avaliadoPorUsuario ?user ;
                    :avaliouFilme ?movie .
        }}
    }}
    """

    results = graph.query(sparql_query)

    recommendations = [str(result.movie_title) for result in results]

    if not recommendations:
        return jsonify({"message": "Nenhuma recomendação encontrada."}), 404

    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
