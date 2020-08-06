from zipfile import ZipFile, ZipInfo
from io import BytesIO


def update_or_insert(path, data):
    """
    Param: path -> file in archive
    Param: data -> data to be updated

    Returns a new zip file with the updated content
    for the given path
    """
    new_zip = BytesIO()

    with ZipFile('config.zip', 'r') as old_archive:
        with ZipFile(new_zip, 'w') as new_archive:
            for item in old_archive.filelist:
                # If you spot an existing file, create a new object
                if item.filename == path:
                    zip_inf = ZipInfo(path)
                    new_archive.writestr(zip_inf, data)
                else:
                    # Copy other contents as it is
                    new_archive.writestr(item, old_archive.read(item.filename))

    return new_zip


new_zip = update_or_insert(
    'docker/docker-compose.yaml',
    b'docker-compose-file-content-new'
)

# Flush new zip to disk
with open('config.zip', 'wb') as f:
    f.write(new_zip.getbuffer())

new_zip.close()
