import pandas as pd
from flask import Flask, request, jsonify, render_template
import joblib

# Cargar los datos de calificaciones y películas con manejo de errores
try:
    ratings_1m = pd.read_csv('data/ratings.dat', sep='::', header=None, 
                             names=['user_id', 'item_id', 'rating', 'timestamp'], engine='python')
    movies_1m = pd.read_csv('data/movies.dat', sep='::', header=None, 
                            names=['item_id', 'title', 'genres'], engine='python', encoding='ISO-8859-1')
except FileNotFoundError as e:
    print(f"Error al cargar los archivos de datos: {e}")
    ratings_1m = None
    movies_1m = None

# Cargar el modelo guardado desde la carpeta /modelo con manejo de errores
try:
    algo = joblib.load('modelo/knn_movie_recommendation_model_1m.pkl')
except FileNotFoundError as e:
    print(f"Error al cargar el modelo: {e}")
    algo = None

app = Flask(__name__)

# Función para obtener las mejores recomendaciones
def get_top_n_recommendations(user_id, n=10):
    if ratings_1m is None or movies_1m is None or algo is None:
        return ["Error: No se pudieron cargar los datos o el modelo."]
    
    # Filtrar las películas que el usuario ya ha visto
    user_ratings = ratings_1m[ratings_1m['user_id'] == user_id]
    all_movies = set(movies_1m['item_id'])
    rated_movies = set(user_ratings['item_id'])
    unrated_movies = list(all_movies - rated_movies)
    
    # Generar predicciones para las películas no vistas
    recommendations = []
    for movie_id in unrated_movies:
        pred = algo.predict(user_id, movie_id)
        recommendations.append((movie_id, pred.est))
    
    # Ordenar las recomendaciones por la calificación estimada
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    # Obtener los títulos de las mejores N recomendaciones
    top_n = recommendations[:n]
    top_n_titles = []
    for movie in top_n:
        title = movies_1m[movies_1m['item_id'] == movie[0]]['title'].values
        if len(title) > 0:
            top_n_titles.append(title[0])
        else:
            top_n_titles.append("Unknown Title")
    
    return top_n_titles

# Ruta principal para mostrar el formulario
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar el formulario e imprimir las recomendaciones
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_id = int(request.form['user_id'])  # Obtener el valor de user_id del formulario
        recommendations = get_top_n_recommendations(user_id, 10)  # Top 10 recomendaciones
        return render_template('index.html', recommendations=recommendations)
    except ValueError as e:
        return jsonify({"error": "Invalid input", "message": str(e)})
    except Exception as e:
        return jsonify({"error": "Something went wrong", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
