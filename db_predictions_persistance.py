from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from prediction_score import Base as Prediction_ScoreBase, PredictionScore
import joblib

# Define the database connection URL
DB_URL = "postgresql://postgres:itba123@localhost:5432/itba_db"

# Create a database engine
engine = create_engine(DB_URL)

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    Prediction_ScoreBase.metadata.create_all(engine)
    print("------------------------------")
    print("PERSISTIENDO PREDICTION_SCORES")
    prediction_scores_dataframe = joblib.load('all_predictions')
    prediction_scores_instances = [PredictionScore.create_object_from_df_row(row) for _, row in prediction_scores_dataframe.iterrows()]
    session.add_all(prediction_scores_instances)

    session.commit()
    session.close()




