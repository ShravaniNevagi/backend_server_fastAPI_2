import tensorflow as tf

def load_model(path="model.h5"):
    model=tf.keras.models.load_model(path)   
    return model


