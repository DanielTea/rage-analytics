from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
np.random.seed(2 ** 10)

# Prevent reaching to maximum recursion depth in `theano.tensor.grad`
# import sys
# sys.setrecursionlimit(2 ** 20)

from six.moves import range

from keras.datasets import cifar10
from keras.layers import Input, Dense, Layer, merge, Activation, Flatten, Lambda
from keras.layers.convolutional import Convolution2D, AveragePooling2D
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.optimizers import SGD
from keras.regularizers import l2
from keras.callbacks import Callback, LearningRateScheduler
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils
import keras.backend as K


batch_size = 32
nb_classes = 7
nb_epoch = 10000
N = 18
weight_decay = 1e-4
lr_schedule = [0.5, 0.75]

death_mode = "lin_decay"  # or uniform
death_rate = 0.5

img_rows, img_cols = 64, 64
img_channels = 3

input_shape = (64, 64, 1)
validation_split = 0.2

from keras.callbacks import CSVLogger, ModelCheckpoint, EarlyStopping
from keras.callbacks import ReduceLROnPlateau
from keras.preprocessing.image import ImageDataGenerator

from models.cnn import mini_XCEPTION
from utils.datasets import DataManager
from utils.datasets import split_data
from utils.preprocessor import preprocess_input

# parameters
patience = 50
base_path = '../trained_models/emotion_models/'

# data generator

# (X_train, y_train), (X_test, y_test) = cifar10.load_data()
# print('X_train shape:', X_train.shape)
# print(X_train.shape[0], 'train samples')
# print(X_test.shape[0], 'test samples')
#
# X_train = X_train.astype('float32')
# X_test = X_test.astype('float32')
#
# # convert class vectors to binary class matrices
# Y_train = np_utils.to_categorical(y_train, nb_classes)
# Y_test = np_utils.to_categorical(y_test, nb_classes)

add_tables = []

inputs = Input(shape=(img_channels, img_rows, img_cols))
# inputs = input_shape

net = Convolution2D(16, 3, 3, border_mode="same", W_regularizer=l2(weight_decay))(inputs)
net = BatchNormalization(axis=1)(net)
net = Activation("relu")(net)


def residual_drop(x, input_shape, output_shape, strides=(1, 1)):
    global add_tables

    nb_filter = output_shape[0]
    conv = Convolution2D(nb_filter, 3, 3, subsample=strides,
                         border_mode="same", W_regularizer=l2(weight_decay))(x)
    conv = BatchNormalization(axis=1)(conv)
    conv = Activation("relu")(conv)
    conv = Convolution2D(nb_filter, 3, 3,
                         border_mode="same", W_regularizer=l2(weight_decay))(conv)
    conv = BatchNormalization(axis=1)(conv)

    if strides[0] >= 2:
        x = AveragePooling2D(strides)(x)

    if (output_shape[0] - input_shape[0]) > 0:
        pad_shape = (1,
                     output_shape[0] - input_shape[0],
                     output_shape[1],
                     output_shape[2])
        padding = K.zeros(pad_shape)
        padding = K.repeat_elements(padding, K.shape(x)[0], axis=0)
        x = Lambda(lambda y: K.concatenate([y, padding], axis=1),
                   output_shape=output_shape)(x)

    _death_rate = K.variable(death_rate)
    scale = K.ones_like(conv) - _death_rate
    conv = Lambda(lambda c: K.in_test_phase(scale * c, c),
                  output_shape=output_shape)(conv)

    out = merge([conv, x], mode="sum")
    out = Activation("relu")(out)

    gate = K.variable(1, dtype="uint8")
    add_tables += [{"death_rate": _death_rate, "gate": gate}]
    return Lambda(lambda tensors: K.switch(gate, tensors[0], tensors[1]),
                  output_shape=output_shape)([out, x])


for i in range(N):
    net = residual_drop(net, input_shape=(16, 32, 32), output_shape=(16, 32, 32))

net = residual_drop(
    net,
    input_shape=(16, 32, 32),
    output_shape=(32, 16, 16),
    strides=(2, 2)
)
for i in range(N - 1):
    net = residual_drop(
        net,
        input_shape=(32, 16, 16),
        output_shape=(32, 16, 16)
    )

net = residual_drop(
    net,
    input_shape=(32, 16, 16),
    output_shape=(64, 8, 8),
    strides=(2, 2)
)
for i in range(N - 1):
    net = residual_drop(
        net,
        input_shape=(64, 8, 8),
        output_shape=(64, 8, 8)
    )

pool = AveragePooling2D((8, 8))(net)
flatten = Flatten()(pool)

predictions = Dense(10, activation="softmax", W_regularizer=l2(weight_decay))(flatten)
model = Model(input=inputs, output=predictions)

sgd = SGD(lr=0.1, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd, loss="categorical_crossentropy")


def open_all_gates():
    for t in add_tables:
        K.set_value(t["gate"], 1)


# setup death rate
for i, tb in enumerate(add_tables, start=1):
    if death_mode == "uniform":
        K.set_value(tb["death_rate"], death_rate)
    elif death_mode == "lin_decay":
        K.set_value(tb["death_rate"], i / len(add_tables) * death_rate)
    else:
        raise


class GatesUpdate(Callback):
    def on_batch_begin(self, batch, logs={}):
        open_all_gates()

        rands = np.random.uniform(size=len(add_tables))
        for t, rand in zip(add_tables, rands):
            if rand < K.get_value(t["death_rate"]):
                K.set_value(t["gate"], 0)

    def on_batch_end(self, batch, logs={}):
        open_all_gates()  # for validation


def schedule(epoch_idx):
    if (epoch_idx + 1) < (nb_epoch * lr_schedule[0]):
        return 0.1
    elif (epoch_idx + 1) < (nb_epoch * lr_schedule[1]):
        return 0.01

    return 0.001

data_generator = ImageDataGenerator(
                        featurewise_center=False,
                        featurewise_std_normalization=False,
                        rotation_range=10,
                        width_shift_range=0.1,
                        height_shift_range=0.1,
                        zoom_range=.1,
                        horizontal_flip=True)


datasets = ['fer2013']
for dataset_name in datasets:
    print('Training dataset:', dataset_name)

    # callbacks
    log_file_path = base_path + dataset_name + '_emotion_training.log'
    csv_logger = CSVLogger(log_file_path, append=False)
    early_stop = EarlyStopping('val_loss', patience=patience)
    reduce_lr = ReduceLROnPlateau('val_loss', factor=0.1, patience=int(patience / 4), verbose=1)
    trained_models_path = base_path + dataset_name + '_mini_XCEPTION'
    model_names = trained_models_path + '.{epoch:02d}-{val_acc:.2f}.hdf5'
    model_checkpoint = ModelCheckpoint(model_names, 'val_loss', verbose=1, save_best_only=True)

    callbacks = [model_checkpoint, csv_logger, early_stop, reduce_lr, GatesUpdate(), LearningRateScheduler(schedule)]

    # loading dataset
    data_loader = DataManager(dataset_name, image_size=input_shape[:2])
    faces, emotions = data_loader.get_data()
    faces = preprocess_input(faces)
    num_samples, num_classes = emotions.shape
    train_data, val_data = split_data(faces, emotions, validation_split)
    train_faces, train_emotions = train_data

    model.fit_generator(data_generator.flow(train_faces, train_emotions,
                                                batch_size, shuffle=True),
                            steps_per_epoch=len(train_faces) / batch_size, nb_epoch=nb_epoch, verbose=1, callbacks=callbacks,
                            validation_data=val_data)


# fit the model on the batches generated by datagen.flow()
# model.fit_generator(datagen.flow(X_train, Y_train, batch_size=batch_size, shuffle=True),
#                     samples_per_epoch=X_train.shape[0],
#                     nb_epoch=nb_epoch,
#                     validation_data=test_datagen.flow(X_test, Y_test, batch_size=batch_size),
#                     nb_val_samples=X_test.shape[0],
#                     callbacks=[GatesUpdate(), LearningRateScheduler(schedule)])