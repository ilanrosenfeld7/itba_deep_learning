from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Enum, PrimaryKeyConstraint, String, Float
from sqlalchemy import desc

Base = declarative_base()


class PredictionScore(Base):
    __tablename__ = 'Prediction_Score'

    movie_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    ratings_pred = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('movie_id', 'user_id'),
    )
    def __init__(self, user_id, movie_id, ratings_pred):
        self.user_id = user_id
        self.movie_id = movie_id
        self.ratings_pred = ratings_pred

    @classmethod
    def create_object_from_df_row(cls, row):
        """
        Crea una instancia de la clase a partir de una fila de un dataframe
        """
        return PredictionScore(row["movie_id"], row["user_id"], row['ratings_pred'])

    @classmethod
    def get_by_user_id_and_ranked_movies(cls, session, user_id, ranked_movies):
        predictions = (session
                       .query(PredictionScore)
                       .filter(PredictionScore.user_id == user_id)
                       .filter(~PredictionScore.movie_id.in_(ranked_movies))
                       .order_by(desc(PredictionScore.ratings_pred))
                       .all())
        rows = [{"movie_id": row.movie_id,
                 "user_id": row.user_id,
                 "ratings_pred": row.ratings_pred
                 }
                for row in predictions]
        return rows