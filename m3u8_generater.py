import sys
import time
import csv
from ad_marker_generetor import get_predicted_labels, merge_cue_markers, \
    remove_other_markers, get_host_path, get_m3u8_body, write_to_local, copy_www

test_url = 'https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/master_360.m3u8'


def get_last_ts_number():
    last_item_index = ''
    last_item = ''
    with open('predict.csv') as csv_file_predict:
        csv_reader_test = csv.reader(csv_file_predict, delimiter=',')
        for row in csv_reader_test:
            last_item = row
        last_item_index = int(last_item[0].split('_')[-1].split('.')[0])
        return last_item_index


def ge_full_url_by_index(body, index):
    lines = body.split('\n')
    format_line = ''
    result = ''
    extra_0 = ''
    for line in lines:
        if ".ts" in line:
            format_line = line
    result = format_line.split('_')[-1]
    offset = format_line.index(result)
    ts = str(index) + '.' + result.split('.')[1]
    if len(str(index)) == 1:
        extra_0 = '0000'
    elif len(str(index)) == 2:
        extra_0 = '000'
    elif len(str(index)) == 3:
        extra_0 = '00'
    elif len(str(index)) == 4:
        extra_0 = '0'
    else:
        extra_0 = ''
    ts = extra_0 + ts
    full_path = format_line[:offset] + ts
    # print full_path
    return full_path


def create_m3u8_with_last(body, n):
    output_str = '#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:6\n#EXT-X-MEDIA-SEQUENCE:'
    last_index = get_last_ts_number()
    start_index = last_index - n
    output_str += str(start_index)
    for i in range(0, n):
        output_str += '\n#EXTINF:6.000,\n'
        output_str += ge_full_url_by_index(body, start_index + i)
    # print output_str
    output_str += '\n'
    return output_str

def get_num_ts(body):
    lines = body.split('\n')
    count = 0
    for line in lines:
        if ".ts" in line:
            count += 1
    return count


def generate(url):
    prefix = get_host_path(url)
    body = get_m3u8_body(url)
    clear_body = remove_other_markers(prefix, body)
    # print clear_body
    predicted_labels = get_predicted_labels(prefix, clear_body)
    rehost_body = create_m3u8_with_last(clear_body, get_num_ts(clear_body))
    write_to_local("output2.m3u8", merge_cue_markers(predicted_labels, rehost_body))
    write_to_local("output.m3u8", clear_body)
    copy_www()

if __name__ == '__main__':
    generate(test_url)

    # args = sys.argv
    # if len(args) > 2:
    #     while True:
    #         generate(args[1], args[2])
    #         time.sleep(6)
    # else:
    #     print 'Fail, params error, try:'
    #     print 'python', args[0], 'your_m3u8_url', 'your_local_dir\n'



