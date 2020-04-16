# Recomander system ( content based method)


import pandas as pd
from math import sqrt
import numpy as np

movies_df = pd.read_csv('ml-latest/movies.csv')
ratings_df = pd.read_csv('ml-latest/ratings.csv')

movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))', '')
movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())
movies_df['genres'] = movies_df.genres.str.split('|')

mv_db = movies_df.copy()

for index, row in movies_df.iterrows():
    for genre in row['genres']:
        mv_db.at[index, genre] = 1
mv_db = mv_db.fillna(0)
ratings_df = ratings_df.drop('timestamp', 1)

userInput = [
            {'title': 'Father of the Bride Part II', 'rating': 4},
            {'title': 'Ace Ventura: When Nature Calls', 'rating': 5},
            {'title': 'How to Make an American Quilt ', 'rating': 2.5},
            {'title': 'Dead Presidents', 'rating': 4.5}
         ]
inputMovies = pd.DataFrame(userInput)

ID = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]
inputMovies = pd.merge(ID, inputMovies)
inputMovies = inputMovies.drop('genres', 1).drop('year', 1)

user_m = mv_db[mv_db['movieId'].isin(inputMovies['movieId'].tolist())]

user_m = user_m.reset_index(drop=True)
userGenreTable = user_m.drop('movieId', 1).drop('title', 1).drop('genres', 1).drop('year', 1)
userProfile = userGenreTable.transpose().dot(inputMovies['rating'])
genreTable = mv_db.set_index(mv_db['movieId'])
genreTable = genreTable.drop('movieId', 1).drop('title', 1).drop('genres', 1).drop('year', 1)
recommendationTable_df = ((genreTable*userProfile).sum(axis=1))/(userProfile.sum())
recommendationTable_df = recommendationTable_df.sort_values(ascending=False)
movies_df.loc[movies_df['movieId'].isin(recommendationTable_df.head(20).keys())]
print(recommendationTable_df)