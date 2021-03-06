"""Backup script.

Uses the Google Drive v3 API service to backup the data from this particular computer to
a unique folder online. We don't do anything fancy here since we are not syncing data
across computers. We also don't allow deleting data from Google Drive; if the data are
deleted locally, they stay on the cloud.

"""
from datetime import datetime
from logging import getLogger
from mimetypes import MimeTypes
from os import walk
from os.path import join as pj
from os.path import split
from pickle import dump
from socket import gethostname

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import client, file, tools

from .paths import credentials_path, data_path, last_backed_up, token_path

logger = getLogger(__name__)
this_computer = gethostname()
mime = "application/vnd.google-apps.%s"
update_files = False


def _build_service() -> object:
    """Returns a service to the Google Drive API."""
    logger.debug("called _build_service()")
    scopes = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
    store = file.Storage(token_path)
    logger.debug("do we have valid local credentials?")
    credentials = store.get()
    if not credentials or credentials.invalid:
        logger.warning("must get credentials")
        flow = client.flow_from_clientsecrets(credentials_path, scopes)
        credentials = tools.run_flow(flow, store)
    logger.debug("credentials received ok, so building service")
    return build("drive", "v3", http=credentials.authorize(Http()))


def _exists(service: object, name: object, parents: object) -> object:
    """Returns the Google Drive item of a file if it exists remotely or None if not.

    Args:
        service:
        name:
        parents:

    Returns:
        object:
    """
    logger.debug("called _exists()")
    q = f"trashed != True"
    for p in parents:
        q += f" and '{p}' in parents"
    q += f" and name = '{name}'"
    items = service.files().list(pageSize=1000, q=q).execute().get("files", [])
    [logger.debug(name + "<->" + i["name"]) for i in items]
    items = [i for i in items if i["name"] == name]
    if len(items) == 0:
        logger.debug(f"no item with name {name} with parents {parents} found")
        return None
    elif len(items) == 1:
        logger.debug(f"item with name {name} with parents {parents} found")
        return items[0]
    else:
        raise IndexError("More than one item found")


def _create_folder(service: object, name: object, parents: object) -> object:
    """Creates a folder in google drive.

    Args:
        service:
        name:
        parents:

    Returns:
        object:
    """
    logger.debug("called _create_folder()")
    item = _exists(service, name, parents)
    if item is None:
        logger.debug(f"creating a folder called {name} with parents {parents}")
        metadata = {"name": name, "parents": parents, "mimeType": mime % "folder"}
        item = service.files().create(body=metadata, fields="id").execute()
    else:
        logger.debug(f"not creating the folder")
    return item


def _upload_file(service: object, name: object, parents: object, path: object) -> None:
    """Uploads a file or folder if it doesn't exist.

    Args:
        service:
        name:
        parents:
        path:
    """
    # TODO: Check files are not identical to those already uploaded
    logger.debug("called _upload_file()")
    metadata = {"name": name, "parents": parents}
    mimetype = MimeTypes().guess_type(name)[0]
    media = MediaFileUpload(path, mimetype=mimetype)
    item = _exists(service, name, parents)
    if item is None:
        logger.debug(f"uploading file")
        service.files().create(body=metadata, media_body=media, fields="id").execute()
    else:
        fid = item["id"]
        if update_files is True:
            logger.debug(f"updating file")
            service.files().update(fileId=fid, media_body=media, fields="id").execute()
        else:
            logger.debug(f"skipping file")


def backup() -> bool:
    """Upload the contents of the local data directory to Google Drive.

    Returns:
        bool: Was the backup successful?

    """
    logger.debug("called backup()")
    service = _build_service()
    logger.debug("creating root remote directory")
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
    logger.debug("all done with backup")
    return True
