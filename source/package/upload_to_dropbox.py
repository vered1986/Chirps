import os
import dropbox

from docopt import docopt

CHUNK_SIZE = 4 * 1024 * 1024


def main():
    """
    Upload the resource file to Dropbox.
    """
    args = docopt("""Upload the resource file to Dropbox.

        Usage: upload_to_dropbox.py <access_token> <resource_dir>

        <access_token>     Access Token.
        <resource_dir>     The resource directory.
    """)

    access_token = args['<access_token>']
    resource_dir = args['<resource_dir>']

    # Connect to dropbox
    client = dropbox.Dropbox(access_token)

    # Read the resource.zip file
    local_file_path = resource_dir + '/resource.zip'
    f = open(local_file_path, 'rb')
    file_size = os.path.getsize(local_file_path)

    db_file_path = '/Chirps/resource.zip'
    mode = dropbox.files.WriteMode('overwrite')

    # Upload in one batch (small file)
    if file_size <= CHUNK_SIZE:
        client.files_upload(f.read(), db_file_path, mode)

    # Upload in chunks
    else:
        upload_session_start_result = client.files_upload_session_start(f.read(CHUNK_SIZE))
        cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
        commit = dropbox.files.CommitInfo(path=db_file_path, mode=mode)

        # Upload more chunks
        while f.tell() < file_size:
            if file_size - f.tell() <= CHUNK_SIZE:
                client.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
            else:
                client.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                cursor.offset = f.tell()


if __name__ == '__main__':
    main()
