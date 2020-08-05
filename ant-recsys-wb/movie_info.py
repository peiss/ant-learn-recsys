import pandas as pd


class MovieInfo(object):
    def __init__(self, fpath):
        self.df = pd.read_csv(fpath)

    def query_by_ids(self, ids):
        target_df = pd.DataFrame(list(ids), columns=["movieId"])
        df_target = pd.merge(left=target_df, right=self.df)

        return df_target

    def get_title_by_id(self, movie_id):
        return self.df[self.df["movieId"] == int(movie_id)]["title"].iloc[0]
