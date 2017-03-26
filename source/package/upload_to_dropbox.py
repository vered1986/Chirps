from docopt import docopt
from dropbox.client import DropboxClient


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

    client = DropboxClient(access_token)
    file = open(resource_dir + '/resource.zip', 'rb')
    client.put_file('resource.zip', file, overwrite=True)


if __name__ == '__main__':
    main()
