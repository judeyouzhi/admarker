from inference import predict, get_filelist
from download_filelist import download_playlist
from m3u8_downloader import is_infile
from m3u8_generater import generate
import sys
import time
import os
import csv


csv_file = 'predict.csv'




def predict_process(path):
    flist = get_filelist(path)
    flist.sort()
    for ts_file in flist:
        if not is_infile(csv_file, ts_file):
            with open(csv_file, mode='a') as csv_file_predict:
                csv_write = csv.writer(csv_file_predict, delimiter=',')
                csv_write.writerow([ts_file, predict(os.path.join(path, ts_file))])


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        file_path = args[2]
        ts_url = args[1]
        access_rights = 0755
        if not os.path.exists(csv_file):
            with open(csv_file, 'w'):
                pass
        try:
            os.mkdir(args[2], access_rights)
        except OSError:
            print ("Creation of the directory %s failed" % file_path)
        else:
            print ("Successfully created the directory %s" % file_path)
        while True:
            download_playlist(ts_url, file_path)
            predict_process(file_path)
            generate(ts_url)
            time.sleep(1)

    else:
        print 'Fail, params error, try:'
        print 'python', args[0], 'dir_your_m3u8_url','dir_save_ts_path', '\n'




