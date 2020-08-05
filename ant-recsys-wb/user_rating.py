import pandas as pd


class UserRating(object):
    def __init__(self, fpath):
        self.df = pd.read_csv(fpath)

    def get_user_watched_ids(self, user_id):
        """用户看过的电影ID列表"""
        return set(self.df[self.df["userId"] == int(user_id)]["movieId"])
