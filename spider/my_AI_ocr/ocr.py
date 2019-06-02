import numpy as np
from PIL import Image
import tensorflow as tf


class OCR():
    def __init__(self):
        self.log_dir = './my_ocr/log/'
        self.N_CLASSES = 10
        self.sess = tf.Session()
        self.ckpt = tf.train.get_checkpoint_state(self.log_dir)
        if self.ckpt and self.ckpt.model_checkpoint_path:
            # 调用saver.restore()函数，加载训练好的网络模型
            print('Loading success')
        else:
            print('No checkpoint')

    def inference(self, images, batch_size, n_classes):
        # conv1, shape = [kernel_size, kernel_size, channels, kernel_numbers]
        with tf.variable_scope("conv1") as scope:
            weights = tf.get_variable("weights",
                                      shape=[3, 3, 3, 16],
                                      dtype=tf.float32,
                                      initializer=tf.truncated_normal_initializer(stddev=0.1, dtype=tf.float32))
            biases = tf.get_variable("biases",
                                     shape=[16],
                                     dtype=tf.float32,
                                     initializer=tf.constant_initializer(0.1))
            conv = tf.nn.conv2d(images, weights, strides=[1, 1, 1, 1], padding="SAME")
            pre_activation = tf.nn.bias_add(conv, biases)
            # 这里用relu激活函数
            conv1 = tf.nn.relu(pre_activation, name="conv1")
        # pool1 && norm1
        with tf.variable_scope("pooling1_lrn") as scope:
            pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                                   padding="SAME", name="pooling1")
            norm1 = tf.nn.lrn(pool1, depth_radius=4, bias=1.0, alpha=0.001 / 9.0,
                              beta=0.75, name='norm1')
        # conv2
        with tf.variable_scope("conv2") as scope:
            weights = tf.get_variable("weights",
                                      shape=[3, 3, 16, 16],
                                      dtype=tf.float32,
                                      initializer=tf.truncated_normal_initializer(stddev=0.1, dtype=tf.float32))
            biases = tf.get_variable("biases",
                                     shape=[16],
                                     dtype=tf.float32,
                                     initializer=tf.constant_initializer(0.1))
            conv = tf.nn.conv2d(norm1, weights, strides=[1, 1, 1, 1], padding="SAME")
            pre_activation = tf.nn.bias_add(conv, biases)
            conv2 = tf.nn.relu(pre_activation, name="conv2")
        # pool2 && norm2
        with tf.variable_scope("pooling2_lrn") as scope:
            pool2 = tf.nn.max_pool(conv2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                                   padding="SAME", name="pooling2")
            norm2 = tf.nn.lrn(pool2, depth_radius=4, bias=1.0, alpha=0.001 / 9.0,
                              beta=0.75, name='norm2')
        # full-connect1
        with tf.variable_scope("fc1") as scope:
            reshape = tf.reshape(norm2, shape=[batch_size, -1])
            dim = reshape.get_shape()[1].value
            weights = tf.get_variable("weights",
                                      shape=[dim, 128],
                                      dtype=tf.float32,
                                      initializer=tf.truncated_normal_initializer(stddev=0.005, dtype=tf.float32))
            biases = tf.get_variable("biases",
                                     shape=[128],
                                     dtype=tf.float32,
                                     initializer=tf.constant_initializer(0.1))
            fc1 = tf.nn.relu(tf.matmul(reshape, weights) + biases, name="fc1")
        # full_connect2
        with tf.variable_scope("fc2") as scope:
            weights = tf.get_variable("weights",
                                      shape=[128, 128],
                                      dtype=tf.float32,
                                      initializer=tf.truncated_normal_initializer(stddev=0.005, dtype=tf.float32))
            biases = tf.get_variable("biases",
                                     shape=[128],
                                     dtype=tf.float32,
                                     initializer=tf.constant_initializer(0.1))
            fc2 = tf.nn.relu(tf.matmul(fc1, weights) + biases, name="fc2")
        # softmax
        with tf.variable_scope("softmax_linear") as scope:
            weights = tf.get_variable("weights",
                                      shape=[128, n_classes],
                                      dtype=tf.float32,
                                      initializer=tf.truncated_normal_initializer(stddev=0.005, dtype=tf.float32))
            biases = tf.get_variable("biases",
                                     shape=[n_classes],
                                     dtype=tf.float32,
                                     initializer=tf.constant_initializer(0.1))
            softmax_linear = tf.add(tf.matmul(fc2, weights), biases, name="softmax_linear")
        return softmax_linear

    def losses(self, logits, labels):
        with tf.variable_scope("loss") as scope:
            # 交叉熵
            cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,
                                                                           labels=labels, name="xentropy_per_example")
            loss = tf.reduce_mean(cross_entropy, name="loss")
            tf.summary.scalar(scope.name + "loss", loss)
        return loss

    def trainning(self, loss, learning_rate):
        with tf.name_scope("optimizer"):
            # 这里可以更换SGD等其他优化方法
            optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            global_step = tf.Variable(0, name="global_step", trainable=False)
            train_op = optimizer.minimize(loss, global_step=global_step)
        return train_op

    def evaluation(self, logits, labels):
        with tf.variable_scope("accuracy") as scope:
            correct = tf.nn.in_top_k(logits, labels, 1)
            correct = tf.cast(correct, tf.float16)
            accuracy = tf.reduce_mean(correct)
            tf.summary.scalar(scope.name + "accuracy", accuracy)
        return accuracy

    def get_one_image(self, img_dir):
        # image = Image.open(img_dir)
        # Image.open()
        # 好像一次只能打开一张图片，不能一次打开一个文件夹，这里大家可以去搜索一下
        image = img_dir.resize([8, 28])
        image_arr = np.array(image)
        return image_arr

    def test(self, test_file):
        # tf.Graph().as_default()
        image_arr = self.get_one_image(test_file)
        image = tf.cast(image_arr, tf.float32)
        image = tf.image.per_image_standardization(image)
        image = tf.reshape(image, [1, 28, 8, 3])

        p = self.inference(image, 1, self.N_CLASSES)
        logits = tf.nn.softmax(p)
        x = tf.placeholder(tf.float32, shape=[28, 8, 3])
        saver = tf.train.Saver()

        sess = tf.Session()
        saver.restore(sess, self.ckpt.model_checkpoint_path)

        prediction = sess.run(logits, feed_dict={x: image_arr})

        max_index = np.argmax(prediction)
        print('the label is:%d' % max_index)
        tf.reset_default_graph()
        return max_index
        # print('the prediction is:')
        # print(prediction)

        # print('This is a %d' %max_index + ' with possibility %.6f' %prediction[:, 0])

    def test_all(self, img_list):
        retlist = []
        for image in img_list:
            retlist.append(self.test(image))

        return retlist


if __name__ == "__main__":
    ocr = OCR()
    print(ocr.test('./test/31.png'))
    # tf.reset_default_graph()
    
    # tf.reset_default_graph()

    imglist = ['./test/30.png', './test/31.png', './test/17.png']
    print(ocr.test_all(imglist))
