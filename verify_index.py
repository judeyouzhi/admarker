import sys


def check(file_path):
    last = 0
    with open(file_path) as log_file:
        lines = log_file.read().split('\n')
        index_num = 0
        log_str = ''
        for line in lines:
            if 'EXTM3U' in line:
                last = 0
            if '#EXT-X-MEDIA-SEQUENCE:' in line:
                log_str = line
            if 'http' in line:
                index_str = line.split('/')[-1]
                index_num = index_str.split('_')[-1].split('.')[0]
                # print last, index_num
                current = int(index_num) - 1
                if not (last == current) and last != 0:
                    print index_num
                    print log_str
                last = int(index_num)


if __name__=='__main__':
    args = sys.argv
    if len(args) > 1:
        check(args[1])
    else:
        print('Params error, try:')
        print('python ', args[0], 'file path')

