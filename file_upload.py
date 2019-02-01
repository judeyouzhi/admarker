import paramiko


host = "ec2-13-115-211-10.ap-northeast-1.compute.amazonaws.com"
port = 22
timeout = 30
user = "jude"
password = "1023729"


def sftp_upload_file(server_path, local_path):
    try:
        k = paramiko.RSAKey.from_private_key_file("/usr/local/google/home/judeyou/ss-aws.pem")
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print "connecting"
        c.connect(hostname=host, username=user, pkey=k)
        print "connected"
        sftp = paramiko.SFTPClient.from_transport(c)
        sftp.put(local_path, server_path)
        c.close()
    except Exception, e:
        print e


if __name__ == '__main__':
    sftp_upload_file("/var/www/html/blm", "t.txt")
