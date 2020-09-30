###############################################################################
# smovie is a cli program to help suggest movies based on your inputs         #
# Developed by: Mo Salam                                                      #
# Email: mosalam208@gmail.com                                                 #
# WebSite: https://mosalam.me                                                 #
###############################################################################
from __future__ import print_function, unicode_literals

import pandas as pd
from imdb import IMDb
import click
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from pandas.core.arrays.sparse import dtype

from pandas.core.reshape.merge import merge

# TODO: later
# how many votes?
# Any Specific Genre? if not then All is default other wise choose from option
# any specific keyword? ex. brad pitt - soap - fight


# cli styling/inputs
style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})


questions = [
    {
        'type': 'input',
        'name': 'smovie_start_year',
        'message': 'What\'s start year? \n',
    },
    {
        'type': 'input',
        'name': 'smovie_end_year',
        'message': 'What\'s end year?, its default to 2020 \n',
    },
    {
        'type': 'list',
        'qmark': '😃',
        'name': 'smovie_score',
        'message': 'IMDB rating above than ... ?',
        'choices': [
            5.0,
            6.0,
            7.0,
            8.0,
            9.0
        ]
    },

]


# start_year = click.prompt('Please tell me the start year', default=1991)
# end_year = click.prompt('End year?', default=2020)
@click.command()
def main():
    answers = prompt(questions)
    pprint(answers)
    movie = Smovie(smovie_start_year=answers['smovie_start_year'],
                   smovie_end_year=answers['smovie_end_year'], smovie_score=answers['smovie_score'])
    print(movie.get_smovie())


if __name__ == "__main__":
    main()


class Smovie:
    """Main Smovie Class that will filter all the data based on the inputs from the user, and return the suggested movie

    """
    MOVIES_RATINGS = pd.read_csv(
        'https://datasets.imdbws.com/title.ratings.tsv.gz', delimiter='\t', compression='gzip', dtype='unicode')
    MOVIES_MAIN = pd.read_csv(
        'https://datasets.imdbws.com/title.basics.tsv.gz', delimiter='\t', compression='gzip', dtype='unicode')
    MOVIES_AKA = pd.read_csv(
        'https://datasets.imdbws.com/title.akas.tsv.gz', delimiter='\t', compression='gzip', dtype='unicode')

    def __init__(self,
                 smovie_type='movie',
                 smovie_id=None,
                 smovie_start_year=1990,
                 smovie_end_year=2020,
                 smovie_primary_language='en',
                 smovie_score=6.0,
                 smovie_votes=None,
                 smovie_genres=[],
                 smovie_imdb_id=None
                 ):
        """Initialize the Smovie class

        Args:
            smovie_id ([string], optional): [imdb ID stripped from the "tt" string]. Defaults to None.
            smovie_start_year (int, optional): [description]. Defaults to 1900.
            smovie_end_year (int, optional): [description]. Defaults to 2020.
            smovie_primary_language (str, optional): [description]. Defaults to 'english'.
            smovie_score (float, optional): [description]. Defaults to 6.0.
            smovie_votes ([type], optional): [description]. Defaults to None.
            smovie_genres (list, optional): [description]. Defaults to [].
        """
        self.smovie_type = smovie_type
        self.smovie_id = smovie_id
        self.smovie_start_year = int(smovie_start_year)
        self.smovie_end_year = int(smovie_end_year)
        self.smovie_primary_language = smovie_primary_language
        self.smovie_score = float(smovie_score)
        self.smovie_votes = smovie_votes
        self.smovie_genres = smovie_genres
        self.smovie_imdb_id = smovie_imdb_id

    def _get_filtered_list(self):
        # subset of a choosen dataset based on the filter inputs
        raw_list = self.MOVIES_MAIN
        movie_type_list = raw_list[raw_list.titleType == 'movie']
        raw_akas_list = self.MOVIES_AKA
        raw_akas_list.rename(columns={'titleId': 'tconst'}, inplace=True)
        raw_ratings_list = self.MOVIES_RATINGS
        startYear = movie_type_list.startYear
        startYear.replace('\\N', '0000', inplace=True)
        # smovie filtered list based on the inputs
        smovie_year_filter = movie_type_list[(startYear.astype('int64')
                                              >= self.smovie_start_year) & (
            startYear.astype('int64') <= self.smovie_end_year)]

        smovie_filtered_with_language = pd.merge(
            raw_akas_list, smovie_year_filter)
        smovie_choosen_language = smovie_filtered_with_language[
            smovie_filtered_with_language.language == self.smovie_primary_language]
        smovie_list = pd.merge(smovie_choosen_language, raw_ratings_list)
        smovie_list_filtered_final = smovie_list[smovie_list.averageRating >=
                                                 self.smovie_score]
        print(smovie_list_filtered_final)
        return smovie_list_filtered_final

    def _get_imdb_url(self):
        # creating the imdb url
        first_part_of_url = 'https://www.imdb.com/title/'
        imdb_url = first_part_of_url + self.smovie_imdb_id + '/'

        return "Click this URL for more information about the movie: " + imdb_url

    def get_smovie(self):

        smovie_list_sample = self._get_filtered_list().sample(5)
        print(smovie_list_sample.head())
        # the choosen movie to be suggested by smovie
        smovie_imdb_id = smovie_list_sample['tconst'].iloc[0]
        self.smovie_imdb_id = smovie_imdb_id
        print(smovie_imdb_id)
        # preparing it for IMDBPY() library it must be without the 'tt' string
        movie_id = smovie_imdb_id.strip('t')

        # tconst = moviesRatings[moviesRatings.tconst == first_value]

        #  create an instance of the IMDb class
        moviesDB = IMDb()
        smovie_value = moviesDB.get_movie(movie_id)

        smovie_summary = smovie_value.summary()
        smovie_result = smovie_summary + '\n' + self._get_imdb_url()
        # show the choosen movie summary in the terminal
        return smovie_result
