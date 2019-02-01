from urlparse import urlparse
from m3u8_downloader import get_host
import requests
import urllib
import os
import sys


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


def get_prefix(url):
	sub = url.split('/')[-1]
	return url[:(url.index(sub))]


def get_index_ts(url):
	sub = url.split('/')[-1]
	temp = sub.split('.')[0].split('_')[-1]
	str_zero = temp[:len(temp)-len(str(int(temp)))]
	prefix_str = sub.split(str_zero)[0]
	return prefix_str+str_zero, int(sub.split('.')[0].split('_')[-1])


def create_url_list(url, size):
	print size
	url_list = []
	prefix = get_prefix(url)
	index_prefix, index_ts = get_index_ts(url)
	url_list.append(url)
	for i in range(1, size):
		new_url = prefix + index_prefix + str(index_ts + i) + ".ts"
		url_list.append(new_url)
	print url_list
	return url_list


def get_m3u8_body(url):
	print 'read m3u8 file:', url
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
		# print '\n[process]: %s/%s' % (i, len(ts_url_list))
		# print '[download]:', ts_url
		# print '[target]:', curr_path
		if os.path.isfile(curr_path):
			# print '[warn]: file already exist'
			continue
                try:
		    urllib.urlretrieve(ts_url, curr_path)
                except urllib.ContentTooShortError:
                    print 'Network conditions is not good.Reloading.'
                    continue

def download_playlist(m3u8_url, download_dir):
	host = get_host(m3u8_url)
	body = get_m3u8_body(m3u8_url)
	ts_url_list = get_url_list(host, body)
	download_ts_file(ts_url_list, download_dir)

def main(url, size, download_dir):
	# host = get_host(url)
	# body = get_m3u8_body(url)
	# ts_url_list = get_url_list(host, body)
	# print 'total file count:', len(ts_url_list)
	ts_url_list = create_url_list(url, int(size))
	download_ts_file(ts_url_list, download_dir)


if __name__ == '__main__':
	args = sys.argv
	if len(args) > 3:
		main(args[1], args[2], args[3])
	else:
		print 'Fail, params error, try:'
		print 'python', args[0], 'your_start_ts_url', 'number_of_ts',  'your_local_dir\n'
