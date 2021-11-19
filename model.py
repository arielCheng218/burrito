
# from train_data import get_training_data
# from keras.models import Sequential
# from keras.layers import Dense

# def model():
#   model = Sequential()
#   model.add(Dense(1048, input_dim=724, activation="relu"))
#   model.add(Dense(500, activation="relu"))
#   model.add(Dense(50, activation="relu"))
#   model.add(Dense(1, activation="softmax"))

#   model.compile(optimizer="adam", loss="mse", metrics=["accuracy"])

#   print("compiled")

#   (X, y) = get_training_data()

#   model.fit(X, y, batch_size=32, epochs=100)