# Task 5 - Hyperparameter tuning
# See results in hype.txt
# We implemented both grid search and random search and used the random search for a reasonably long search
# for the best hyperparameters. Due to time and compute limitations we were a bit constrained in our tuning,
# we focused on tuning the initial learning rate for Adam optimizer as we have seen adam to be
# consistently better than Gradient descent and to tune dropout rate only for the final layer as we have
# seen too much underfitting when using dropout in all layers.
# The method of grid search is to do a brute-force search on a grid for all possible parameter combinations,
# and finally the parameter combination that gave the best result on the validation-dataset
# is returned. Randomised search is a stochastic procedure, where hyper-parameters are
# sampled from some specified distribution. After a certain amount of sampling the best
# set of parameters are returned.

from __future__ import print_function

# all tensorflow api is accessible through this
import tensorflow as tf
# to visualize the resutls
import matplotlib.pyplot as plt
import numpy as np
# 70k mnist dataset that comes with the tensorflow container
from tensorflow.examples.tutorials.mnist import input_data

# Enable deterministic comparisons between executions
tf.set_random_seed(0)
# constants
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE * IMAGE_SIZE
NUM_CLASSES = 10
NUM_TRAINING_ITER = 10000
NUM_EPOCH_SIZE = 100
NUM_HIDDEN_1 = 200
NUM_HIDDEN_2 = 100
NUM_HIDDEN_3 = 60
NUM_HIDDEN_4 = 30
GD_LEARNING_RATE = 0.5

# load data
mnist = input_data.read_data_sets('../data/fashion', one_hot=True, validation_size=0)
print('Number of train examples in dataset ' + str(len(mnist.train.labels)))
print('Number of test examples in dataset ' + str(len(mnist.test.labels)))

def define_placeholders():
    # Define placeholders for input data and for input truth labels
    x = tf.reshape(tf.placeholder(tf.float32, [None, IMAGE_SIZE, IMAGE_SIZE, 1]),
                   [-1, IMAGE_PIXELS])  # training examples (just one color channel, i.e grayscale)
    y_ = tf.placeholder(tf.float32, [None, NUM_CLASSES])  # correct answers(labels)

    return x, y_


def build_graph(x, dropout_rate):
    # Helper function for weight variables, random gaussian weight initialization with 0 mean.
    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)


    # Helper function for bias variables, random gaussian weight initialization with 0 mean.
    def bias_variable(shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)


    # Helper function for convolutional layers with specified input size, stride
    # conv2d performs 2D convolution on 4D input, if input is 5D one can use 3D convolution
    # conv2d essentially means that the patch is strided over 2d surface for all input channels.
    # SAME padding means that zero-padding will be used on borders when patch does not fit perfectly on surface.
    def conv2d(x, W, stride):
        return tf.nn.conv2d(x, W, strides=stride, padding='SAME')


    x_image = tf.reshape(x, [-1, 28, 28, 1]) # [numImages, height, width, channels]

    # Layer 1 - Convolutional, 5x5 patch strided 1 pixel at a time over the input,
    # 1 input channel of size 28x28,
    # 4 output channels per feature, feature map size 28x28
    # output_height = in_height/strides[1] = 28/1 = 28
    # output_width = in_width/strides[2] = 28/1 = 28
    W_conv1 = weight_variable([5, 5, 1, 4])
    b_conv1 = bias_variable([4])

    # Layer 2 - Convolutional, 5x5 patch strided 2 pixels at a time over the input,
    # 4 input channels of size 28x28,
    # 8 output channels per feature, feature map size is 14x14
    # output_height = in_height/strides[1] = 28/2 = 14
    # output_width = in_width/strides[2] = 28/2 = 14
    W_conv2 = weight_variable([5, 5, 4, 8])
    b_conv2 = weight_variable([8])

    # Layer 3 - Convolutional, 5x5 patch strided 2 pixels at a time over the input,
    # 9 input channels of size 28x28,
    # 12 output channels per feature, feature map size is 7x7
    # output_height = in_height/strides[1] = 14/2 = 7
    # output_width = in_width/strides[2] = 14/2 = 7
    W_conv3 = weight_variable([4, 4, 8, 12])
    b_conv3 = weight_variable([12])

    # Layer 4 - Fully connected,
    # 12 input channels of size 7x7,
    # 200 output channels, flattened
    W_fc = weight_variable([7 * 7 * 12, 200])
    b_fc = weight_variable([200])

    # Activation layer - Softmax
    # 200 input channels
    # 10 output channels, one per class
    W_fc2 = weight_variable([200, NUM_CLASSES])
    b_fc2 = bias_variable([NUM_CLASSES])

    # 2. Define the model - compute predicitions

    # hidden layers with relu, 3 convolutional layer and 1 FC layer
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1, [1, 1, 1, 1]) + b_conv1)
    #h_conv1 = tf.nn.dropout(h_conv1, keep_prob=DROPOUT_RATE)

    h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2, [1, 2, 2, 1]) + b_conv2)
    #h_conv2 = tf.nn.dropout(h_conv2, keep_prob=DROPOUT_RATE)

    h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3, [1, 2, 2, 1]) + b_conv3)
    #h_conv3 = tf.nn.dropout(h_conv3, keep_prob=DROPOUT_RATE)
    h_conv3_flat = tf.reshape(h_conv3, [-1, 7 * 7 * 12])

    # Hidden FC layer output
    h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flat, W_fc) + b_fc)
    h_fc1 = tf.nn.dropout(h_fc1, keep_prob=dropout_rate)

    # Readout/Softmax layer

    # Compute the logits, aka the inverse of the sigmoid/softmax outputs for the softmax layer
    logits = tf.matmul(h_fc1, W_fc2) + b_fc2

    return logits


def define_optimizer(learning_rate, logits, labels):
    # Define the loss, which is the loss between softmax of logits and the labels
    # Tensorflow performs softmax (the output activation) as part of the loss for efficiency
    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=logits, name='xentropy'))

    # 4. Define the accuracy
    # Correct prediction is black/white, either the classification is correct or not
    # Accuracy is the ratio of correct predictions over wrong predictions
    correct_predictions = tf.equal(tf.argmax(logits, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))

    # Exponential decay of learning rate (task 3)
    global_step = tf.Variable(0, trainable=False)
    starter_learning_rate = learning_rate
    learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step, 500, 0.96, staircase=True)

    # 5. Train with an Optimizer

    # task 1
    #train_step = tf.train.GradientDescentOptimizer(GD_LEARNING_RATE).minimize(cross_entropy_loss)

    # task 2
    #train_step = tf.train.AdamOptimizer(ADAM_LEARNING_RATE).minimize(cross_entropy_loss)

    # task 3
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy_loss, global_step=global_step)
    #train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(cross_entropy_loss, global_step=global_step)

    return train_step, accuracy, cross_entropy_loss

def init_graph():
    # initialize and run start operation
    init = tf.global_variables_initializer()
    sess = tf.Session()
    sess.run(init)

    return sess


# Function representing a single iteration during training.
# Returns a tuple of accuracy and loss statistics.
def training_step(update_test_data, update_train_data, images, labels, training_step, accuracy, cross_entropy_loss, sess):
    # actual learning
    # reading batches of 100 images with 100 labels
    batch_X, batch_Y = mnist.train.next_batch(100)
    # the backpropagation training step
    sess.run(training_step, feed_dict={images: batch_X, labels: batch_Y})

    # evaluating model performance for printing purposes
    # evaluation used to later visualize how well you did at a particular time in the training
    train_a = []  # Array of training-accuracy for a single iteration
    train_c = []  # Array of training-cost for a single iteration
    test_a = []  # Array of test-accuracy for a single iteration
    test_c = []  # Array of test-cost for a single iteration

    # If stats for train-data should be updates, compute loss and accuracy for the batch and store it
    if update_train_data:
        train_acc, train_cos = sess.run([accuracy, cross_entropy_loss], feed_dict={images: batch_X, labels: batch_Y})
        train_a.append(train_acc)
        train_c.append(train_cos)

    # If stats for test-data should be updates, compute loss and accuracy for the batch and store it
    if update_test_data:
        test_acc, test_cos = sess.run([accuracy, cross_entropy_loss],
                                      feed_dict={images: mnist.test.images, labels: mnist.test.labels})
        test_a.append(test_acc)
        test_c.append(test_cos)

    return train_a, train_c, test_a, test_c


# 6. Train and test the model, store the accuracy and loss per iteration

def hype_grid():
    learning_rates = [0.0001, 0.001, 0.003, 0.05, 0.03]
    dropout_rates = [0.1, 0.2, 0.3, 0.6, 0.8]

    for learning_rate in learning_rates:
        for dropout_rate in dropout_rates:
            print("Trying following " + str(learning_rate) + " learning rate and " + str(dropout_rate) + ' dropout rate')
            test_accuracy = main(learning_rate, dropout_rate)
            print('Test accuracy ' + str(test_accuracy[-1]))


def hype_random():
    learning_rates = np.random.uniform(0.0001, 0.03, 10).tolist()
    dropout_rates = np.random.uniform(0.1, 0.8, 10).tolist()

    for learning_rate in learning_rates:
        for dropout_rate in dropout_rates:
            print("Trying following " + str(learning_rate) + " learning rate and " + str(dropout_rate) + ' dropout rate')
            test_accuracy = main(learning_rate, dropout_rate)
            print('Test accuracy ' + str(test_accuracy[-1]))


def main(learning_rate, dropout_rate):
    train_accuracy = []
    train_cost = []
    test_accuracy = []
    test_cost = []

    images, labels = define_placeholders()
    logits = build_graph(images, dropout_rate)
    training_step_tf, accuracy, cross_entropy_loss = define_optimizer(learning_rate, logits, labels)
    sess = init_graph()

    for i in range(NUM_TRAINING_ITER):
        test = False
        if i % NUM_EPOCH_SIZE == 0:
            test = True
            print("iter: " + str(i))
        a, c, ta, tc = training_step(test, test, images, labels, training_step_tf, accuracy, cross_entropy_loss, sess)
        train_accuracy += a
        train_cost += c
        test_accuracy += ta
        test_cost += tc

    plot(train_accuracy, train_cost, test_accuracy, test_cost)

    sess.close()

    return test_accuracy

def plot(train_accuracy, train_cost, test_accuracy, test_cost):
    # 7. Plot and visualise the accuracy and loss

    print('Final test accuracy ' + str(test_accuracy[-1]))
    print('Final test loss ' + str(test_cost[-1]))

    # accuracy training vs testing dataset
    plt.plot(train_accuracy, label='Train data')
    plt.xlabel('Epoch')
    plt.plot(test_accuracy, label='Test data')
    plt.ylabel('Accuracy')
    plt.grid(True)
    plt.legend()
    plt.title('Accuracy per epoch train vs test')
    plt.show()

    # loss training vs testing dataset
    plt.plot(train_cost, label='Train data')
    plt.plot(test_cost, label='Test data')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Loss per epoch, train vs test')
    plt.grid(True)
    plt.show()

    # Zoom in on the tail of the plots
    zoom_point = 50
    x_range = range(zoom_point, int(NUM_TRAINING_ITER / NUM_EPOCH_SIZE))
    plt.plot(x_range, train_accuracy[zoom_point:])
    plt.plot(x_range, test_accuracy[zoom_point:])
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Accuracy per epoch train vs test')
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.plot(train_cost[zoom_point:])
    plt.plot(test_cost[zoom_point:])
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Loss per epoch train vs test')
    plt.legend()
    plt.grid(True)
    plt.show()


#hype_random()
main(learning_rate=0.0115649014129, dropout_rate=0.709008503773)