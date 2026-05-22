"""
Test script to review a movie using OMDB API.
"""

import requests
import os

# Set API keys
os.environ['OMDB_API_KEY'] = 'a5a24a4b'
os.environ['DEEPSEEK_API_KEY'] = 'sk-30c0248809ec4596b00f767199e98576'

# Test OMDB API
api_key = os.environ.get('OMDB_API_KEY')
movie_title = 'Fight Club'

print(f'Testing review for: {movie_title}')
print('='*50)

# Fetch movie data
r = requests.get('http://www.omdbapi.com/', params={'apikey': api_key, 't': movie_title, 'plot': 'full'})
data = r.json()

if data.get('Response') == 'True':
    print(f'Title: {data.get("Title")}')
    print(f'Year: {data.get("Year")}')
    print(f'IMDB: {data.get("imdbRating")}/10')
    print(f'Director: {data.get("Director")}')
    print(f'Cast: {data.get("Actors")}')
    print(f'Genre: {data.get("Genre")}')
    print(f'Runtime: {data.get("Runtime")}')
    print(f'Plot: {data.get("Plot")[:200]}...')
    print(f'Poster: {data.get("Poster")}')
    print()
    print('OMDB API working correctly!')
else:
    print(f'Error: {data.get("Error")}')
