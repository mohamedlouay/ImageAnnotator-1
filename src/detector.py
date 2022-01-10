import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import numpy as np

# kernel_size: dimension of the filter matrix /
model = models.Sequential(
    [
        # cnn
        layers.Conv2D(
            filters=32, kernel_size=(3, 3), activation="relu", input_shape=(32, 32, 3)
        ),
        layers.MaxPooling2D((2, 2)),
        # dense
        layers.Flatten(),
        layers.Dense(64, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ]
)

model.compile(
    optimizer="adam", loss="sparsq_categorical_crossentropy", metrics=["accuracy"]
)
