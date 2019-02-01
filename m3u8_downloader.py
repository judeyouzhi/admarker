from urlparse import urlparse
import requests
import urllib
import os
import sys
import time
import csv


g_body = '''#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:7
#EXT-X-MEDIA-SEQUENCE:174709

#EXT-X-CUE-OUT-CONT:CAID=0x0100,ElapsedTime=100.167,Duration=120,SCTE35=/DAuAAAAAAAAAP/wBQb/q31bBgAYAhZDVUVJABaqwX/DAACky3UMAgEANAAASLlijQ==
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00709.ts
#EXT-X-CUE-OUT-CONT:CAID=0x0100,ElapsedTime=106.173,Duration=120,SCTE35=/DAuAAAAAAAAAP/wBQb/q31bBgAYAhZDVUVJABaqwX/DAACky3UMAgEANAAASLlijQ==
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00710.ts
#EXT-X-CUE-OUT-CONT:CAID=0x0100,ElapsedTime=112.179,Duration=120,SCTE35=/DAuAAAAAAAAAP/wBQb/q31bBgAYAhZDVUVJABaqwX/DAACky3UMAgEANAAASLlijQ==
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00711.ts
#EXT-X-CUE-OUT-CONT:CAID=0x0100,ElapsedTime=118.185,Duration=120,SCTE35=/DAuAAAAAAAAAP/wBQb/q31bBgAYAhZDVUVJABaqwX/DAACky3UMAgEANAAASLlijQ==
#EXTINF:1.802,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00712.ts
#EXT-X-CUE-IN
#EXTINF:4.204,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00713.ts
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00714.ts
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00715.ts
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00716.ts
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00717.ts
#EXTINF:6.006,
https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/20190103T024256/master_360/00087/master_360_00718.ts'''


# AD_SIGNAL_MARKER = 'CUE-OUT'
AD_SIGNAL_MARKER = 'ANVATO-SPOT'

def is_infile(file_name, ts_name):
    with open(file_name) as csv_file_predict:
        csv_reader_test = csv.reader(csv_file_predict, delimiter=',')
        for row in csv_reader_test:
            if ts_name == row[0]:
                return True
        return False


def get_url_list(host, body):
	lines = body.split('\n')
	ts_url_list = []
	flag_ads = 0
	for line in lines:
		if AD_SIGNAL_MARKER in line:
			flag_ads = 1
		if not line.startswith('#') and line != '':
			if line.startswith('http'):
				ts_url_list.append((line, flag_ads))

			else:
				ts_url_list.append(('%s/%s' % (host, line), flag_ads))
			flag_ads = 0
	return ts_url_list


def get_host(url):
	urlgroup = urlparse(url)
	# return urlgroup.scheme + '://' + urlgroup.hostname
	return 'https://anv-bloomberg-iflix-asia.storage.googleapis.com/live/ephemeral/j3zMBknHpRKeBs8W1q6H0NM7WIQ05kyl/iflix/3096k'


def get_m3u8_body(url):
	print 'read m3u8 file:', url
	session = requests.Session()
	adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=10)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	r = session.get(url, timeout=10)
	return r.content


def save_ts_label(ts_name, label_name):
	if not is_infile('truth.csv', ts_name):
		with open('truth.csv', mode='a') as csv_file_truth:
			csv_write = csv.writer(csv_file_truth, delimiter=',')
			csv_write.writerow([ts_name, label_name])


def download_ts_file_by_category(ts_url_list, download_dir):
	i = 0
	for ts_url_i in sorted(ts_url_list, key=lambda url: url[0]):
		ts_url = ts_url_i[0]
		is_ads = ts_url_i[1]
		i += 1
		file_name = ts_url[ts_url.rfind('/'):]
		if is_ads:
			curr_path = '%s%s' % (download_dir + '/ads', file_name)
			save_ts_label(file_name[1:], 'ads')
		else:
			curr_path = '%s%s' % (download_dir + '/content', file_name)
			save_ts_label(file_name[1:], 'content')
# comment out below while serving
# 		print '\n[process]: %s/%s' % (i, len(ts_url_list))
# 		print '[download]:', ts_url
# 		print '[target]:', curr_path
# 		if os.path.isfile(curr_path):
# 			print '[warn]: file already exist'
# 			continue
# 		urllib.urlretrieve(ts_url, curr_path)


def main(url, download_dir):
	if not os.path.exists(download_dir):
		with os.mkdir(download_dir, 755):
			pass
	if not os.path.exists('truth.csv'):
		with open('truth.csv', 'w'):
			pass
	host = get_host(url)
	body = get_m3u8_body(url)
	#body = g_body
	ts_url_list = get_url_list(host, body)
	for line in ts_url_list: print line
	print 'total file count:', len(ts_url_list)
	download_ts_file_by_category(ts_url_list, download_dir)


if __name__ == '__main__':
	args = sys.argv
	if len(args) > 2:
		# main(args[1], args[2])
		while True:
			main(args[1], args[2])
			time.sleep(6)
	else:
		print 'Fail, params error, try:'
		print 'python', args[0], 'your_m3u8_url', 'your_local_dir\n'