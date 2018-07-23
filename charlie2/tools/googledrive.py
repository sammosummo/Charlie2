"""Backup script.

Uses the Google Drive v3 API service to backup the data from this particular computer to
a unique folder online. We don't do anything fancy here since we are not syncing data
across computers. We also don't allow deleting data from Google Drive; if the data are
deleted locally, they stay on the cloud.

"""
from datetime import datetime
from logging import getLogger
from os import walk
from os.path import split, join as pj
from pickle import dump
from socket import gethostname
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from httplib2 import Http
from mimetypes import MimeTypes
from oauth2client import file, client, tools
from .paths import data_path, last_backed_up, credentials_path, token_path


logger = getLogger(__name__)
this_computer = gethostname()
mime = "application/vnd.google-apps.%s"


def _build_service():
    """Returns a service to the Google Drive API."""
    logger.info("called _build_service()")
    scopes = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
    store = file.Storage(token_path)
    logger.info("do we have valid local credentials?")
    credentials = store.get()
    if not credentials or credentials.invalid:
        logger.warning("must get credentials")
        flow = client.flow_from_clientsecrets(credentials_path, scopes)
        credentials = tools.run_flow(flow, store)
    logger.info("credentials received ok, so building service")
    return build("drive", "v3", http=credentials.authorize(Http()))


def _exists(service, name, parents):
    """Returns the Google Drive item of a file if it exists remotely or None if not."""
    logger.info("called _exists()")
    q = f"trashed != True"
    for p in parents:
        q += f" and '{p}' in parents"
    items = service.files().list(pageSize=100, q=q).execute().get("files", [])
    items = [i for i in items if i["name"] == name]
    if len(items) == 0:
        return None
    elif len(items) == 1:
        return items[0]
    else:
        raise IndexError("More than one item found")


def _create_folder(service, name, parents):
    """Creates a folder in google drive."""
    logger.info("called _create_folder()")
    item = _exists(service, name, parents)
    if item is None:
        metadata = {"name": name, "parents": parents, "mimeType": mime % "folder"}
        item = service.files().create(body=metadata, fields="id").execute()
    return item


def _upload_file(service, name, parents, path):
    """Uploads a file or folder if it doesn't exist."""
    logger.info("called _upload_file()")
    metadata = {"name": name, "parents": parents}
    mimetype = MimeTypes().guess_type(name)[0]
    media = MediaFileUpload(path, mimetype=mimetype)
    item = _exists(service, name, parents)
    if item is None:
        service.files().create(body=metadata, media_body=media, fields="id").execute()
    else:
        fid = item["id"]
        service.files().update(fileId=fid, media_body=media, fields="id").execute()


def backup():
    """Upload the contents of the local data directory to Google Drive."""
    logger.info("called backup()")
    service = _build_service()
    logger.info("creating root remote directory")
    item = _create_folder(service, this_computer, [])
    parent_ids = {"data": item["id"]}

    for root, _, files in walk(data_path):

        parent_dir, last_dir = split(root)
        _, parent_dir = split(parent_dir)

        if parent_dir != "charlie2":

            parent = parent_ids[parent_dir]
            item = _create_folder(service, last_dir, [parent])
            parent_ids[last_dir] = item["id"]

            for name in [f for f in files if f != ".gitignore"]:

                p = pj(root, name)
                _upload_file(service, name, [item["id"]], p)

    dump(datetime.now(), open(last_backed_up, "wb"))
    logger.info("all done with backup")
    return True
