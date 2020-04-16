
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
movies_df = movies_df.drop('genres', 1)


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
inputMovies = inputMovies.drop('year', 1)

Sub_user = ratings_df[ratings_df['movieId'].isin(inputMovies['movieId'].tolist())]
group_sub_user = Sub_user.groupby(['userId'])
group_sub_user = sorted(group_sub_user,  key=lambda x: len(x[1]), reverse=True)
group_sub_user = group_sub_user[0:100]

CorrelationDict = {}

for name, group in group_sub_user:
    group = group.sort_values(by='movieId')
    inputMovies = inputMovies.sort_values(by='movieId')
    nRatings = len(group)
    temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]
    tempRatingList = temp_df['rating'].tolist()
    tempGroupList = group['rating'].tolist()
    Sxx = sum([i ** 2 for i in tempRatingList]) - pow(sum(tempRatingList), 2) / float(nRatings)
    Syy = sum([i ** 2 for i in tempGroupList]) - pow(sum(tempGroupList), 2) / float(nRatings)
    Sxy = sum(i * j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList) * sum(tempGroupList) / float(
        nRatings)

    if Sxx != 0 and Syy != 0:
        CorrelationDict[name] = Sxy / sqrt(Sxx * Syy)
    else:
        CorrelationDict[name] = 0


CorrelationDict.items()

data_person = pd.DataFrame.from_dict(CorrelationDict, orient='index')
data_person.columns = ['similarityIndex']
data_person['userId'] = data_person.index
data_person.index = range(len(data_person))

Top = data_person.sort_values(by='similarityIndex', ascending=False)[0:50]
Top_user_rate = Top.merge(ratings_df, left_on='userId', right_on='userId', how='inner')
Top_user_rate['weightedRating'] = Top_user_rate['similarityIndex']*Top_user_rate['rating']
tempTopUsersRating = Top_user_rate.groupby('movieId').sum()[['similarityIndex', 'weightedRating']]
tempTopUsersRating.columns = ['sum_similarityIndex', 'sum_weightedRating']


recom = pd.DataFrame()
recom['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
recom['movieId'] = tempTopUsersRating.index
recommendation_df = recom.sort_values(by='weighted average recommendation score', ascending=False)
movies_df.loc[movies_df['movieId'].isin(recommendation_df.head(10)['movieId'].tolist())]
print(recom)