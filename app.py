import pandas as pd
from flask import Flask, request, jsonify
import joblib

try:
    ratings_1m = pd.read_csv('data/ratings.dat', sep='::', header=None, names=['user_id', 'item_id', 'rating', 'timestamp'], engine='python')
    movies_1m = pd.read_csv('data/movies.dat', sep='::', header=None, names=['item_id', 'title', 'genres'], engine='python', encoding='ISO-8859-1')
except FileNotFoundError as e:
    print(f"Error: {e}")

# Cargar el modelo guardado desde la carpeta /model
algo = joblib.load('modelo/knn_movie_recommendation_model_1m.pkl')

app = Flask(__name__)

def get_top_n_recommendations(user_id, n=10):
    user_ratings = ratings_1m[ratings_1m['user_id'] == user_id]
    all_movies = set(movies_1m['item_id'])
    rated_movies = set(user_ratings['item_id'])
    unrated_movies = list(all_movies - rated_movies)
    
    recommendations = []
    for movie_id in unrated_movies:
        pred = algo.predict(user_id, movie_id)
        recommendations.append((movie_id, pred.est))
    
    recommendations.sort(key=lambda x: x[1], reverse=True)
    top_n = recommendations[:n]
    top_n_titles = [movies_1m[movies_1m['item_id'] == movie[0]]['title'].values[0] for movie in top_n]
    return top_n_titles

@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = int(request.args.get('user_id'))
    n = int(request.args.get('n', 10))
    recommendations = get_top_n_recommendations(user_id, n)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
