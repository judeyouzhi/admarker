from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import pandas as pd
import argparse
import sys,os
import csv
import tensorflow as tf
from PIL import Image
from tqdm import tqdm

from get_key_frame import get_i_keyframes

# t=tqdm(pd.read_csv('test.csv').values)
# test=[]
#
# i=0
#
# for tt in t:
#     test.append(tt[0])
#     i+=1

def get_filelist(dir):
    for dirpath, dirnames, filenames in os.walk(dir):
        # print dirpath, dirnames, filenames, '\n'
        return filenames




def load_image(filename):
    #Read in the image_data to be classified."""
    return tf.gfile.FastGFile(filename, 'rb').read()

def load_labels(filename):
    #Read in labels, one label per line."""
    return [line.rstrip() for line in tf.gfile.GFile(filename)]

def load_graph(filename):
    #Unpersists graph from file as default graph."""
    with tf.gfile.FastGFile(filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')


def run_graph(src, dest, labels, input_layer_name, output_layer_name, num_top_predictions):
    with tf.Session() as sess:
        # Feed the image_data as input to the graph.
        # predictions  will contain a two-dimensional array, where one
        # dimension represents the input image count, and the other has
        # predictions per class
        i = 0
        # with open('submit.csv','w') as outfile:
        for f in os.listdir(src):
            # im = Image.open(os.path.join(src, f))
            # img = im.convert('RGB')
            # img.save(os.path.join(dest, test[i] + '.jpg'))
            image_data = load_image(os.path.join(dest, test[i] + '.jpg'))
            softmax_tensor = sess.graph.get_tensor_by_name(output_layer_name)
            predictions, = sess.run(softmax_tensor, {input_layer_name: image_data})

            # Sort to show labels in order of confidence
            top_k = predictions.argsort()[-num_top_predictions:][::-1]
            for node_id in top_k:
                predicted_label = labels[node_id]
                score = predictions[node_id]
                # print(test[i] + ',', predicted_label)
                # outfile.write(test[i]+','+human_string+'\n')
            i += 1


def load_test_csv(path_to_data):
    for item in os.listdir(path_to_data):
        for filename in get_filelist(os.path.join(path_to_data, item)):
            if '.jpg' in filename:
                save_ouput_csv('data.csv', filename, item)


def save_ouput_csv(filename, image_name, predicted_label):
    with open(filename, mode='a') as result_file:
        result_writer = csv.writer(result_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        result_writer.writerow([image_name, predicted_label])


def performance_evaluate(test_file, result_file):
    data = []
    result = []
    d = {}
    r = {}
    allfiles = []
    error_count = 0
    line_count_test = 0
    line_count_result = 0
    with open(test_file) as csv_file_test:
        csv_reader_test = csv.reader(csv_file_test, delimiter=',')
        for row in csv_reader_test:
            d[row[0]] = row[1]
            # data.append(d)
            allfiles.append(row[0])
            line_count_test += 1
    with open(result_file) as csv_file_result:
        csv_reader_result = csv.reader(csv_file_result, delimiter=',')
        for row in csv_reader_result:
            r[row[0]] = row[1]
            # result.append(r)
            line_count_result += 1
    if line_count_test != line_count_test:
        print('WARNING: result size error')
    for filename in allfiles:
        if d[filename] != r[filename]:
            error_count += 1
            print(filename)
            print('Train set:' + d[filename] + ' but classified as:' + r[filename])
            print("accuracy:= " + str(float(1-error_count/line_count_test)))


def run_new_graph(src, dest, labels, input_layer_name, output_layer_name, num_top_predictions):
    with tf.Session() as sess:
        for filename in get_filelist(src):
            # im = Image.open(os.path.join(src, f))
            # img = im.convert('RGB')
            # img.save(os.path.join(dest, test[i] + '.jpg'))
            print(os.path.join(src, filename))
            image_data = load_image(os.path.join(src, filename))
            softmax_tensor = sess.graph.get_tensor_by_name(output_layer_name)
            input_layer_tensor = sess.graph.get_tensor_by_name(input_layer_name)
            predictions, = sess.run(softmax_tensor, {input_layer_tensor: image_data})

            # Sort to show labels in order of confidence
            top_k = predictions.argsort()[-num_top_predictions:][::-1]
            for node_id in top_k:
                predicted_label = labels[node_id]
                score = predictions[node_id]
                print(filename + ',', predicted_label)
                save_ouput_csv('result.csv', filename, predicted_label)


ts_label = {"ads": 0, "content": 0}

def ts_decision_record(label):
    global ts_label
    ts_label[label] += 1


def ts_decision():
    result = ''
    if ts_label['ads'] >= ts_label['content']:
        result = 'ads'
    else:
        result = 'content'
    ts_label['ads'] = 0
    ts_label['content'] = 0
    return result


def init_graph():
    global ready_to_serve
    if ready_to_serve != 1:
        load_graph(graph)
        ready_to_serve = 1
    return


def predict(input_ts):
    init_graph()
    frames = get_i_keyframes(input_ts)
    with tf.Session() as sess:
        # print(input_ts)
        for frame_data in frames:
            # image_data = load_image(input_ts)
            filename = frame_data[0]
            image_data = load_image(filename)
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            input_layer_tensor = sess.graph.get_tensor_by_name('DecodeJpeg/contents:0')
            predictions, = sess.run(softmax_tensor, {input_layer_tensor: image_data})
            # Sort to show labels in order of confidence
            top_k = predictions.argsort()[-num_top_predictions:][::-1]
            for node_id in top_k:
                predicted_label = labels[node_id]
                score = predictions[node_id]
                print(filename + ',\t', predicted_label + ' \tscore: ' + str(score))
            if os.path.exists(filename):
                os.remove(filename)
                ts_decision_record(predicted_label)
    return ts_decision()


src = os.path.join('.', 'tmp/test/all')
dest = os.path.join('.', 'tmp/test/output')
labels = 'output_labels.txt'
graph = 'output_graph.pb'
input_layer = 'DecodeJpeg/contents:0'
output_layer = 'final_result:0'
num_top_predictions = 1
labels = load_labels(labels)
ready_to_serve = 0
# run_graph(src, dest, labels, input_layer, output_layer, num_top_predictions)
# if os.path.exists("result.csv"):
#     os.remove("result.csv")
# if os.path.exists("data.csv"):
#     os.remove("data.csv")
# load_test_csv('tmp/test/data')
# run_new_graph(src, dest, labels, input_layer, output_layer, num_top_predictions)
# performance_evaluate('data.csv', 'result.csv')

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        # save_i_keyframes(args[1])
        load_graph(graph)
        print (predict(args[1]))
    else:
        print('Fail, params error, try:')
        print('python', args[0], 'dir_your_ts_path', '\n')

