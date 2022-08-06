from fastapi import FastAPI,Response, status, HTTPException
import pandas as pd 
from pydantic import BaseModel
from fastapi.params import Body
import pickle
import json
import requests

app = FastAPI()

movies_df = pickle.load(open('movies.pkl','rb'))

class Post(BaseModel):
    title: str
    


df = movies_df [['movie_id', 'title']]
results = df.to_json(orient='records')
movies_list_json = json.loads(results)

similarity = pickle.load(open('similarity.pkl','rb'))
movies_list = movies_df['title'].values


def fetch_poster(movie_id):
    resposne = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=879e0a6b6320e78680c5b9d2f132d406&language=en-US'.format(movie_id))
    data = resposne.json()

    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']

def recommand(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)),reverse=True,key = lambda x:x[1])[1:6]
    

    recommanded_movies = []
    recommanded_movies_posters = []
    movie_ids = []
    for i in movies_list:
        #fetch poster from api
        movie_id = movies_df.iloc[i[0]].movie_id
        recommanded_movies.append(movies_df.iloc[i[0]].title)
        recommanded_movies_posters.append(fetch_poster(movie_id))
        movie_ids.append(movie_id)

    recommanded_movies_dict = {'movie_id':movie_ids, 'movies':recommanded_movies, 'posters':recommanded_movies_posters}
    return pd.DataFrame(recommanded_movies_dict)




#path operaton/route
@app.get('/') #for get method
async def root(): #for asyncrones and it can be removed and still work
    return {'message':'Hello FastAPI!'}




@app.get('/list')
def get_posts():
    return {'data':movies_list_json}






@app.get('/list/{movie_id}') #path parameter
def get_post(movie_id: str):#, response: Response):


    movie_name = df[df['movie_id'] == int(movie_id)].title.to_list()[0]

    recommanded_movie_df = recommand(movie_name)
    results = recommanded_movie_df.to_json(orient='records')
    recommanded_movie_json = json.loads(results)
    if not recommanded_movie_json:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f'post with id: {id} was not found'}
        raise HTTPException(status_code  = status.HTTP_404_NOT_FOUND, detail = 'None')
    return {'post_details':recommanded_movie_json}






