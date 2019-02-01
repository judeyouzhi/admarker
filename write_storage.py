from google.cloud import storage


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    client = storage.Client.from_service_account_json('/usr/local/google/home/judeyou/judeyou-dai-e8c8b4659f9d.json')
    """Uploads a file to the bucket."""
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    blob.make_public()
    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))




if __name__ == '__main__':
    # list_blobs('judeyou-dai')
    # explicit()
    # write_master()


    upload_blob('cue-gen', 'master.m3u8', 'master.m3u8')