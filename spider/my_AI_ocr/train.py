import pickle  
import os
import numpy as np
from PIL import Image
import tensorflow as tf
import matplotlib.pyplot as plt
import time
import ocr

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
start = time.clock()
def print_time():
    print(time.clock()-start)

def get_index(str):
    index = str.split(sep='.')
    return (int)(index[0])

def get_files(files_dir):
    image_list = []
    temp_list = sorted(os.listdir(files_dir),key=get_index)
    image_list = [files_dir+filename for filename in temp_list]

    label_list = []
    label_list = [int(i) for i in list(data.values())]

    return image_list, label_list
    
def get_batch(image,label,image_W,image_H,batch_size,capacity):
    image = tf.cast(image,tf.string)
    label = tf.cast(label,tf.int32)
    
    #tf.cast()用来做类型转换
    input_queue = tf.train.slice_input_producer([image,label])
    #加入队列
    label = input_queue[1]
    image_contents = tf.read_file(input_queue[0])
    image = tf.image.decode_png(image_contents,channels=3)
    #png或者jpg格式都用decode_png函数，其他格式可以去查看官方文档
    image = tf.image.resize_image_with_crop_or_pad(image,image_W,image_H)
    #resize
    image = tf.image.per_image_standardization(image)
    #对resize后的图片进行标准化处理
    image_batch,label_batch = tf.train.batch([image,label],batch_size = batch_size,num_threads=16,capacity = capacity)
    label_batch = tf.reshape(label_batch,[batch_size])
    return image_batch,label_batch
    #获取两个batch，两个batch即为传入神经网络的数据


def inference(images, batch_size, n_classes):
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
        #这里用relu激活函数
        conv1 = tf.nn.relu(pre_activation, name="conv1")
    # pool1 && norm1
    with tf.variable_scope("pooling1_lrn") as scope:
        pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                               padding="SAME", name="pooling1")
        norm1 = tf.nn.lrn(pool1, depth_radius=4, bias=1.0, alpha=0.001/9.0,
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
        norm2 = tf.nn.lrn(pool2, depth_radius=4, bias=1.0, alpha=0.001/9.0,
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


def losses(logits, labels):
    with tf.variable_scope("loss") as scope:
        #交叉熵
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,
                                                                       labels=labels, name="xentropy_per_example")
        loss = tf.reduce_mean(cross_entropy, name="loss")
        tf.summary.scalar(scope.name + "loss", loss)
    return loss

def trainning(loss, learning_rate):
    with tf.name_scope("optimizer"):
      #这里可以更换SGD等其他优化方法
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        global_step = tf.Variable(0, name="global_step", trainable=False)
        train_op = optimizer.minimize(loss, global_step=global_step)
    return train_op

def evaluation(logits, labels):
    with tf.variable_scope("accuracy") as scope:
        correct = tf.nn.in_top_k(logits, labels, 1)
        correct = tf.cast(correct, tf.float16)
        accuracy = tf.reduce_mean(correct)
        tf.summary.scalar(scope.name + "accuracy", accuracy)
    return accuracy


def random_batch(X_train, y_train, batch_size):
    rnd_indices = np.random.randint(0, len(X_train), batch_size)
    X_batch = X_train[rnd_indices]
    y_batch = y_train[rnd_indices]
    return X_batch, y_batch

def run_training():
    logs_train_dir = './log/'
    #存放一些模型文件的目录
    train,train_label = get_files(train_dir)
    train_batch,train_label_batch =  get_batch(train,train_label,IMG_W,IMG_H,BATCH_SIZE,CAPACITY)
    
    train_logits =inference(train_batch,BATCH_SIZE,N_CLASSES)
    train_loss = losses(train_logits,train_label_batch)
    train_op = trainning(train_loss,learning_rate)
    train_acc = evaluation(train_logits,train_label_batch)
    summary_op = tf.summary.merge_all()
    sess = tf.Session()
    train_writer = tf.summary.FileWriter(logs_train_dir,sess.graph)
    #saver主要用来保存和加载模型
    saver = tf.train.Saver()
    sess.run(tf.global_variables_initializer())
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess = sess,coord = coord)
    try:
        for step in np.arange(MAX_STEP):
            #
            #
            if coord.should_stop():
                break
            _,tra_loss,tra_acc = sess.run([train_op,train_loss,train_acc])
            #每迭代50次，打印出一次结果
            if step %  50 == 0:
                print('Step %d,train loss = %.2f,train accuracy = %.2f'%(step,tra_loss,tra_acc))
                summary_str = sess.run(summary_op)
                train_writer.add_summary(summary_str,step)
            if step % 200 ==0 or (step +1) == MAX_STEP:
                checkpoint_path = os.path.join(logs_train_dir,'model.ckpt')
                saver.save(sess,checkpoint_path,global_step = step)
                #每迭代200次，利用saver.save()保存一次模型文件，以便测试的时候使用
    except tf.errors.OutOfRangeError:
        print('Done training epoch limit reached')
    finally:
        coord.request_stop()
    coord.join(threads)
    sess.close()

def get_one_image(img_dir):
     image = Image.open(img_dir)
     #Image.open()
     #好像一次只能打开一张图片，不能一次打开一个文件夹，这里大家可以去搜索一下
     image = image.resize([8, 28])
     image_arr = np.array(image)
     return image_arr

def test(test_file):
    log_dir = './log/'
    image_arr = get_one_image(test_file)
    image = tf.cast(image_arr, tf.float32)
    image = tf.image.per_image_standardization(image)
    image = tf.reshape(image, [1,28, 8, 3])

    p = inference(image,1,N_CLASSES)
    logits = tf.nn.softmax(p)
    x = tf.placeholder(tf.float32,shape = [28,8,3])
    saver = tf.train.Saver()

    with tf.Session() as sess:
        ckpt = tf.train.get_checkpoint_state(log_dir)
        if ckpt and ckpt.model_checkpoint_path:
            global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
            #调用saver.restore()函数，加载训练好的网络模型
            saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            print('No checkpoint')
        prediction = sess.run(logits, feed_dict={x: image_arr})

        max_index = np.argmax(prediction) 
        # print('the label is:')
        print(max_index)
        # print('the prediction is:')
        # print(prediction)
        # print('This is a %d' %max_index + ' with possibility %.6f' %prediction[:, 0])
        
        return max_index

if __name__ == "__main__":
    train_dir = './img_rec/'
    data = pickle.load(open('map.pkl','rb'))  

    N_CLASSES = 10
    BATCH_SIZE = 7900
    CAPACITY = 64
    IMG_W = 28  #图片的宽和高
    IMG_H = 8
    MAX_STEP = 1000
    #迭代一千次，如果机器配置好的话，建议至少10000次以上
    learning_rate = 0.0001
    #学习率

    image_list,label_list = get_files(train_dir)
    # image_batch,label_batch = get_batch(image_list,label_list,IMG_W,IMG_H,BATCH_SIZE,CAPACITY)

    # with tf.Session() as sess:
    #     i=0
    #     coord = tf.train.Coordinator()
    #     threads = tf.train.start_queue_runners(coord = coord)
    #     try:
    #         while not coord.should_stop() and i<2:
    #         #提取出两个batch的图片并可视化。
    #             img,label = sess.run([image_batch,label_batch])
    #             for j in np.arange(BATCH_SIZE):
    #                 print('label: %d'%label[j])
    #                 plt.imshow(img[j,:,:,:])
    #                 plt.show()
    #             i+=1
    #     except tf.errors.OutOfRangeError:
    #         print('done!')
    #     finally:
    #         coord.request_stop()
    #     coord.join(threads)

    # run_training()
    # test('./test/30.png')
    # tf.reset_default_graph()

    # 测试准确率
    # start = time.clock()
    out=[]
    ocr = ocr.OCR()
    i=0
    for image in image_list:
        if(i==7000):
            break
        out.append(ocr.test(image))
        # tf.reset_default_graph()
        i=i+1
    # print_time()
    i=0
    j=0
    for i in range(len(label_list)):
        if(i==7000):
            break
        if(out[i]==label_list[i]):
            j=j+1

    print('accuracy is %.2f'%(j/i))
    # start = time.clock()

    # ocr = ocr.OCR()
    # print(ocr.test_all(image_list[0:500]))
    # print_time()