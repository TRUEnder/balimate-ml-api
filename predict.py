import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer

# Local module
from handler.preprocessing import preprocessingWithStem
from handler.loadDataset import loadDestinations


# Predict User Rating Function

def predict(userid, have_not_visited_place_ids):

    # Load tourism data from local
    tourism = pd.read_csv('destination.csv', encoding='latin-1')

    # #  Data preprocessing

    # data_tourism = tourism.copy()
    # data_tourism.description = data_tourism.description.apply(
    #     preprocessingWithStem)

    # # TF-IDF matrix
    # tfidf_vectorizer = TfidfVectorizer()
    # tfidf_matrix = tfidf_vectorizer.fit_transform(data_tourism['description'])

    # input_data adalah deretan destination yang belum pernah dikunjungi user
    input_data = tourism[tourism['place_id'].isin(
        have_not_visited_place_ids['place_id'])]

    # Load tfidf matrix from extracting the feature of place description
    tfidf_df = pd.read_csv('tfidf_description.csv')
    tfidf_matrix = np.full(
        (input_data.shape[0], tfidf_df.shape[1]), tfidf_df.to_numpy())
    user_id_column = np.full(input_data.shape[0], float(userid))

    # Recreate the exact same model, including its weights and the optimizer
    hybrid_model = tf.keras.models.load_model('hybrid_model.h5')

    # Melakukan prediksi rating untuk tempat yang belum dikunjungi
    predicted_ratings = hybrid_model.predict(
        [tfidf_matrix, user_id_column, input_data['place_id'].values.reshape(-1)])
    # Membatasi nilai dalam rentang [0, 5]
    predicted_ratings = np.clip(predicted_ratings, 0, 5)
    # Menykalakan nilai ke rentang [0, 5]
    predicted_ratings = (predicted_ratings / np.max(predicted_ratings)) * 5

    # Membuat DataFrame dengan kolom 'Place_Name' dan 'Predicted_Rating'
    predictions_df = input_data.copy()
    predictions_df['predicted_rating'] = predicted_ratings.flatten()

    # Mengurutkan predictions_df berdasarkan 'Predicted_Rating' secara menurun
    predictions_df = predictions_df.sort_values(
        by='predicted_rating', ascending=False).head(10)

    # Hapus kolom predicted_rating
    predictions_df = predictions_df.loc[:,
                                        predictions_df.columns != 'predicted_rating']

    # Menampilkan prediksi
    return predictions_df.to_dict('records')