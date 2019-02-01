from urlparse import urlparse
#from write_storage import upload_blob
import requests
import urllib
import os
import sys
import time
import csv
import subprocess

'''
This script use below as test stream: 
https://anv-bloomberg-iflix-asia.storage.googleapis.com/live/ephemeral/j3zMBknHpRKeBs8W1q6H0NM
7WIQ05kyl/iflix/3096k/index.m3u8?userid=v_122-i_122&assetid=122
'''


def write_master():
    f = open("./master.m3u8", "w")
    f.write("#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-INDEPENDENT-SEGMENTS\n#EXT-X-STREAM-INF:BANDWIDTH=800000,"
            "AVERAGE-BANDWIDTH=800000\noutput2.m3u8")
    f.flush()
    f.close()


def write_to_local(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.flush()
    f.close()


def copy_www():
    #subprocess.run('cp output2.m3u8 /var/www/html')
    #subprocess.run('cp master.m3u8 /var/www/html')
    os.system('cp output.m3u8 /var/www/html')
    os.system('cp output2.m3u8 /var/www/html')
    os.system('cp master.m3u8 /var/www/html')
    

def is_cue_in(seg_length, line):
    current = get_current_offset(line)
    duration = get_ad_duration(line)
    if seg_length > duration - current:
        return True
    else:
        return False


# def replace_ad_markers(prefix, body):
#     newbody = ''
#     lines = body.split('\n')
#     for line in lines:
#         if ".ts" in line:
#             line = prefix + line
#
#         if line.startswith('#ANVATO-SPOT') and line != '':
#             # print line
#             duration = get_ad_duration(line)
#             if "pos=0" in line:
#                 line = "#EXT-X-CUE-OUT:DURATION=" + str(duration)
#                 line += '\n'
#             elif is_cue_in(6, line):
#                 line = "#EXT-X-CUE-IN"
#                 line += '\n'
#             else:
#                 line = ''
#         else:
#             line += '\n'
#         newbody += line
#     return newbody


def remove_other_markers(prefix, body):
    newbody = ''
    lines = body.split('\n')
    for line in lines:
        # if ".ts" in line:
        #     line = prefix + line
        #     print line

        if line.startswith('#ANVATO-SPOT') or line.startswith('#EXT-X-CUE-OUT')\
                or line.startswith('#EXT-X-CUE-IN') \
                or line.startswith('#EXT-OATCLS-SCTE35')\
                or line.startswith('#EXT-X-ASSET')\
                and line != '':
            line = ''
            # print line
            # duration = get_ad_duration(line)
            # if "pos=0" in line:
            #     line = "#EXT-X-CUE-OUT:DURATION=" + str(duration)
            #     line += '\n'
            # elif is_cue_in(6, line):
            #     line = "#EXT-X-CUE-IN"
            #     line += '\n'
            # else:
            #     line = ''
        else:
            line += '\n'
        newbody += line
    return newbody


def get_predict_label(ts_file):
    with open('predict.csv') as csv_file_predict:
        csv_reader_test = csv.reader(csv_file_predict, delimiter=',')
        for row in csv_reader_test:
            if ts_file == row[0]:
                return row[1]
        return 'undefined'


last_label = 'content'
labels = ['']
count = 100


def record_last_5_labels(the_label, the_list):
    if len(the_list) > 4:
        for i in range(0, len(the_list) - 4):
            the_list.pop(i)
    the_list.append(the_label)
    return the_list


def get_predicted_labels(prefix, body):
    predicted_labels = []
    clear_body = remove_other_markers(prefix, body)
    lines = clear_body.split('\n')
    for line in lines:
        if 'http' in line:
            current_label = get_predict_label(line.split('/')[-1])
            if current_label == 'undefined':
                break
            else:
                predicted_labels.append(current_label)
    return predicted_labels


def merge_cue_markers(predict_labels, body):
    # if len(set(predict_labels)) == 1:
    #     # print body
    #     return body
    items = body.split('ts')
    # if len(predict_labels) < len(items):
    #     print 'predicting, skip'
    #     return ''
    result = ''
    final = ''
    for i in range(len(predict_labels) - 1):
        if predict_labels[i] == 'content' and predict_labels[i + 1] == 'ads':
            result += items[i]
            result += '\n#EXT-X-CUE-OUT:DURATION=120'
        elif predict_labels[i] == 'ads' and predict_labels[i + 1] == 'content':
            result += items[i]
            result += '\n#EXT-X-CUE-IN'
        else:
            result += items[i]
#    for j in range(len(predict_labels) - 1, len(items)):
#        result += items[j]
    for line in result.split('\n'):
        if line.startswith('http'):
            line += 'ts'
        line += '\n'
        final += line
    # print '\ninsert markers:\n'
    # print final
    return final


def insert_cue_markers(prefix, body):
    clear_body = remove_other_markers(prefix, body)
    return merge_cue_markers(get_predicted_labels(prefix, clear_body), clear_body)


# def insert_cue_markers(prefix, body):
#     global last_label, labels, count
#     add_once_flag = True
#     clear_body = remove_anvato_markers(prefix, body)
#     newbody = ''
#     lines = clear_body.split('\n')
#
#     for line in lines:
#         current_label = ''
#         if 'http' in line:
#             current_label = get_predict_label(line.split('/')[-1])
#             if current_label == 'undefined':
#                 break
#             print current_label, add_once_flag, labels, count, last_label
#             if current_label == 'ads' and add_once_flag and labels.pop() == 'content':
#                 print 'ad insert here'
#                 line += "\n#EXT-X-CUE-OUT:DURATION=120"
#                 add_once_flag = False
#                 count = 1
#             if current_label == 'content' and add_once_flag and labels.pop() == 'ads':
#             # if count == 15:
#                 line = "#EXT-X-CUE-IN\n"
#                 add_once_flag = False
#             count += 1
#             labels = record_last_5_labels(current_label, labels)
#             last_label = current_label
#         line += '\n'
#         newbody += line
#     return newbody


def get_ad_duration(line):
    words = line.split('=')
    return int(words[1].split('/')[1].split(',')[0])


def get_current_offset(line):
    words = line.split('=')
    return int(words[1].split('/')[0])


def get_url_list(host, body):
    lines = body.split('\n')
    ts_url_list = []
    for line in lines:
        if not line.startswith('#') and line != '':
            if line.startswith('http'):
                ts_url_list.append(line)
            else:
                ts_url_list.append('%s/%s' % (host, line))
    return ts_url_list


def get_host(url):
    urlgroup = urlparse(url)
    return urlgroup.scheme + '://' + urlgroup.netloc


def get_host_path(url):
    urlgroup = urlparse(url)
    urlpath = urlgroup.path
    length_m3u8 = len(urlpath.split("/")[-1])
    path_prefix = urlpath[:-length_m3u8]
    return get_host(url) + path_prefix

def get_m3u8_body(url):
    # print 'read m3u8 file:', url
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=10)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    r = session.get(url, timeout=10)
    return r.content


def download_ts_file(ts_url_list, download_dir):
    i = 0
    for ts_url in reversed(ts_url_list):
        i += 1
        file_name = ts_url[ts_url.rfind('/'):]
        curr_path = '%s%s' % (download_dir, file_name)
        print '\n[process]: %s/%s' % (i, len(ts_url_list))
        print '[download]:', ts_url
        print '[target]:', curr_path
        if os.path.isfile(curr_path):
            print '[warn]: file already exist'
            continue
        urllib.urlretrieve(ts_url, curr_path)


def main(url, download_dir):
    host = get_host(url)
    prefix = get_host_path(url)
    # print host
    body = get_m3u8_body(url)
    # print body
    #ts_url_list = get_url_list(host, body)
    result = insert_cue_markers(prefix, body)
    if '' != result:
        write_to_local("output2.m3u8", result)
        write_master()
        copy_www()
    # print "\nreplaced:"
    # print result
    # print "\n============================\n"
    #print 'total file count:', len(ts_url_list)
    #download_ts_file(ts_url_list, download_dir)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        while True:
            main(args[1], args[2])
            time.sleep(6)
    else:
        print 'Fail, params error, try:'
        print 'python', args[0], 'your_m3u8_url', 'your_local_dir\n'

