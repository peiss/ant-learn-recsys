from flask import Flask

from embedding_manager import EmbeddingManager
from movie_info import MovieInfo
from user_rating import UserRating

app = Flask(__name__)

"""
加载资源到内存，这些资源真实情况下可能存储于mysql/redis
但如果业务不大，都加载到内存速度最快！
"""
print("load user embedding")
mgr_user_embedding = EmbeddingManager(
    "./resources/user_embedding.csv", "id", "features")

print("load movie embedding")
mgr_movie_embedding = EmbeddingManager(
    "./resources/item_embedding.csv", "id", "features")

print("load movie embedding")
obj_user_rating = UserRating("./resources/ratings.csv")

print("load movie info")
obj_movie_info = MovieInfo("./resources/movies.csv")


@app.route("/")
def index():
    return "hello"


@app.route('/guess_like/<user_id>')
def guess_like(user_id):
    # 1. 获取该用户的embedding
    user_embedding_str = mgr_user_embedding.get_embedding(user_id)

    # 2. 获取该用户看过的电影ID列表
    watch_ids = obj_user_rating.get_user_watched_ids(user_id)

    # 3. 使用近邻搜索获取用户可能喜欢的电影ID列表
    target_movie_ids = mgr_movie_embedding.search_ids_by_embedding(user_embedding_str,
                                                                   2 * len(watch_ids))
    # 4. 去除已经看过的列表
    target_movie_ids = [x for x in target_movie_ids if x not in watch_ids]

    # 5. 拼接电影标题，返回给客户端
    movie_html_list = get_movie_list_html(target_movie_ids)

    return f"""
        <h1>用户自己的embedding：</h1>
        <div>{user_embedding_str}</div>

        <h1>用户看过的ID列表：</h1>
        <div>{watch_ids}</div>
        
        <h1>猜你喜欢：</h1>
        {movie_html_list}
    """


@app.route("/related_rec/<movie_id>")
def query_movie_related_rec(movie_id):
    # 查询自己的embedding
    movie_embedding = mgr_movie_embedding.get_embedding(movie_id)

    # 查询相似的电影
    movie_ids = mgr_movie_embedding.search_ids_by_embedding(movie_embedding, 10)

    # 查询电影名称信息列表
    movie_html_list = get_movie_list_html(movie_ids)

    # 查询电影标题
    movie_title = obj_movie_info.get_title_by_id(movie_id)

    # 拼接内容返回结果
    return f"""
        <h1>电影名：{movie_title}</h1>
        <h1>电影ID：{movie_id}</h1>

        <h1>电影embedding：</h1>
        <div>{movie_embedding}</div>
        
        <h1>相关推荐：</h1>
        {movie_html_list}
    """


def get_movie_list_html(movie_ids):
    """
    根据电影ID，拼接电影标题，返回HTML
    """
    df_result = obj_movie_info.query_by_ids(movie_ids)
    df_result = df_result[["movieId", "title"]].head(10)

    rec_table = """
            <table>
                <tr>    
                    <th>电影ID</th>
                    <th>电影标题</th>
                    <th>查看</th>
                </tr>
            """
    for idx, row in df_result.iterrows():
        rec_table += f"""
                <tr>    
                    <td>{row["movieId"]}</td>
                    <td>{row["title"]}</td>
                    <td><a href="/related_rec/{row["movieId"]}">查看</a></td>
                </tr>
            """

    rec_table += """</table>"""

    return f"""<div>{rec_table}</div>"""


if __name__ == '__main__':
    # 启动服务
    app.run(host="0.0.0.0", port=9999)
