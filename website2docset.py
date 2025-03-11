#!/usr/bin/env python3

"""website2docset

Converts the HTML,CSS,JS directory to a Docset by
1.create the Docset Folder
2.copy files into the Docset Folder
3.create info.plist Docset metadata
4.create the SQLite index Database
5.create the meta.json file for the Docset metadata

Usage:
    website2docset.py -n VHDL93 -v 0.0 -i icon.png HDL-Docs\

    VHDL93: the name for the Docset to create
    0.0: the Docset version
    icong.png: the icon to add to the Docset
    HDL-Docs: the HTML,CSS,JS directory
"""

import argparse
import os
import re
import sys
import sqlite3
import shutil
import logging
from contextlib import contextmanager
from PIL import Image
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import Fore, Style
import colorama

VERSION = 0.0
MAX_ICON_SIZE: int = 16
INDEX_FILE: str = "index.html"

colorama.init()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def db_connection(db_path):
    """trying to connect to the sqlite3 db.

        Args:
            sqlite_path(str): the path to the dsidx file.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        yield conn
    except sqlite3.Error as e:
        logger.error(f"{Fore.RED}Database error: {e}{Style.RESET_ALL}")
        raise
    finally:
        if conn:
            conn.close()


def init_db(db):
    """initialize the database with required table and index.

        Args:
            db (Connection): SQLite connection object.
    """
    cur = db.cursor()
    try:
        # Drop existing table if it exists
        cur.execute('DROP TABLE IF EXISTS searchIndex;')
        # Create the table
        cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        # Create the index
        cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
        db.commit()
    except sqlite3.Error as e:
        logger.error(f"{Fore.RED}Error initializing database: {e}{Style.RESET_ALL}")
        raise


def update_db(db, name: str, class_attr: str, path: str):
    """add to database to allows Dash to index search

    Args:
        db(Connection): SQLite connection object.

        name(str): the name of the entry.
        for example,if you are adding a function, it would be the name of the function.

        class_attr(str): a HTML class attribute to define the type of the entry
        For example,if you are adding a Section(HTML),it would be "Section"
        for a list of types that Dash recognize, see https://kapeli.com/docsets#supportedentrytypes

        path(str): is the relative path towards the documentation file you want Dash
        to display for this entry.it can contain an anchor(#) or also a supports "http://"
        URL entries.
    """
    cur = db.cursor()
    try:
        cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
        dbpath = cur.fetchone()
        cur.execute("SELECT rowid FROM searchIndex WHERE name = ?", (name,))
        dbname = cur.fetchone()
        if dbpath is None and dbname is None:
            cur.execute('INSERT OR IGNORE INTO searchIndex (name, type, path) VALUES (?,?,?)', (name, class_attr, path))
        else:
            pass
    except Exception as e:
        logger.error(f"{Fore.RED}Error updating database: {e}{Style.RESET_ALL}")


def add_urls(path_dsidx: str, path_docset: str):
    """parse the index HTML file to create the Database
        by Extracting all class attribute for the Docset.
        for the class attribute see https://kapeli.com/docsets#supportedentrytypes

        Args:
            path_dsidx(str): the path to the dsidx file.
            path_docset(str): path to the docset folder

    """
    # connect to database
    with db_connection(path_dsidx) as db:
        # initialize the database with required table
        init_db(db)

        with open(os.path.join(path_docset, INDEX_FILE), encoding="utf-8") as file:
            index = file.read()

            soup = BeautifulSoup(index, "html.parser")
            found = re.compile('.*')
            for tag in soup.find_all('a', {'href': found}):
                name = tag.text.strip()
                if len(name) > 0:
                    path = tag.attrs['href'].strip()
                    if path.split('#')[0] not in (INDEX_FILE):
                        # Extract class attribute for the Docset
                        class_attr = tag.attrs.get('class', ['Section'])[0]  # Default to 'Section' if class is not present
                        # update db
                        update_db(db, name, class_attr, path)
            db.commit()


def add_infoplist(path_info: str, doc_name: str):
    """create the info.plist file to describes the Docset metadata

        Args:
            path_info(str): path where to create the info file.
            doc_name(str): the name of the docset.

    """
    name = doc_name.split('.')[0]
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
    <dict>
        <key>CFBundleIdentifier</key>
        <string>{name}</string>
        <key>CFBundleName</key>
        <string>{name.capitalize()}</string>
        <key>DocSetPlatformFamily</key>
        <string>{name}</string>
        <key>isDashDocset</key><true/>
        <key>dashIndexFilePath</key>
        <string>index.html</string>
        <key>DashDocSetBlocksOnlineResources</key><true/>
        <key>isJavaScriptEnabled</key><true/>
    </dict>
</plist>

    """
    try:
        open(path_info, 'w', encoding="utf-8").write(info_plist)
        print(f"{Fore.GREEN}Create the Info.plist File{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{Fore.RED}**Error**:  Create the Info.plist File Failed...{Style.RESET_ALL}")
        logger.error(e)
        clear_trash()
        sys.exit(2)


def add_meta(path_info: str, name: str, version: float = 0.0):
    """create the meta.json file for the Docset metadata

        Args:
            path_info(str): path to write the meta data
            name(str): the Docset name
            version(float): the number version for the Docset
    """

    meta = f"""
    {{
        "extra":{{
            "keywords": [
            "vhdl93",
            "vhdl",
            "VHDL93",
            "VHDL"
        ],
        "indexFilePath": "INDEX_FILE"
        }},
        "name": "{name}",
        "title": "{name}",
        "revision": "{version}"
    }}"""

    try:
        open(path_info, 'w', encoding="utf-8").write(meta)
        print(f"{Fore.GREEN}Create the meta.json File{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{Fore.RED}**Error**: Create the meta.json File Failed...{Style.RESET_ALL}")
        logger.error(e)
        clear_trash()
        sys.exit(2)


def check_icon_size(path_icon: str, size:int) -> bool:
    """check if icon meets the size requirements 16x16 pixels.

        Args:
            path_icon(str): Path to the icon file.
            size(int): the size that icon need to match

        Returns:
            bool: True if the size is 16x16 pixels,False otherwise.

        Raises:
            PIL.UnidentifiedImageError: If image format is invalid
            FileNotFoundError: If the icon file doesn't exist
    """
    try:
        with Image.open(path_icon) as img:
            width, height = img.size
            if width == size and height == size:
                return True

            logger.warning(f"{Fore.YELLOW}**Warning**: Image size must be {size} pixels.{Style.RESET_ALL}")
            logger.warning(f"{Fore.YELLOW}but Current size is: {width}x{height}! No icon will be generated.{Style.RESET_ALL}")
            return False
    except Exception as e:
        logger.error(f"{Fore.RED}Error opening image: {e}{Style.RESET_ALL}")
        clear_trash()
        sys.exit(2)


def copy_docs(dir_source: str, docset_dir: str) -> None:
    """copy the HTML,CSS,JS files into Docset folder.

        Args:
            dir_source(str): the source folder of the website docs.
            docset_dir(str): the destination docset folder.

    """

    if not os.path.exists(docset_dir):
        os.makedirs(docset_dir)
        print(f"{Fore.GREEN}Create the Docset Folder!{Style.RESET_ALL}")
        for subdir in tqdm(os.listdir(dir_source)):
             # skip vscode folder
            if '.vscode' in subdir:
                continue
            try:
                shutil.copytree(os.path.join(dir_source, subdir), os.path.join(docset_dir, subdir))
            except NotADirectoryError as not_dir:
                try:
                    shutil.copy(os.path.join(dir_source, subdir), os.path.join(docset_dir, subdir))
                except Exception as e:
                    clear_trash()
                    logger.error(f"{Fore.RED}{e}{Style.RESET_ALL}")
                    raise Exception(f"{Fore.RED}**Error**:  Copy Html Documents Failed...{Style.RESET_ALL}") from not_dir
    else:
        print(f"{Fore.YELLOW}The Docset Folder already exists!{Style.RESET_ALL}")
        exit(0)


def clear_trash():
    """clear useless files"""
    try:
        shutil.rmtree(docset_name)
        logger.info(f"{Fore.RED}Clear generated useless files!{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{Fore.RED}**Error**:  Clear trash failed...{Style.RESET_ALL}")
        logger.error(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='Name the docset explicitly')
    parser.add_argument('-d', '--destination', dest='path', default='', help='Put the resulting docset into PATH')
    parser.add_argument('-i', '--icon', dest='filename', help='Add PNG icon FILENAME to docset')
    parser.add_argument('-p', '--index-page', help='Set the file that is shown')
    parser.add_argument('-v', '--version', dest='version', help='the version of the Docset')
    parser.add_argument('SOURCE', help='Directory containing the HTML,CSS,JS documents')
    results = parser.parse_args()

    source_dir = results.SOURCE
    if source_dir[-1] == os.sep:
        source_dir = results.SOURCE[:-1]

    if not os.path.exists(source_dir):
        print(source_dir + " does not exist!")
        sys.exit(2)

    dir_name = os.path.basename(source_dir)
    if not results.name:
        docset_name = dir_name + ".docset"
    else:
        docset_name = results.name + ".docset"

    doc_path = os.path.join(docset_name, "Contents", "Resources", "Documents")
    dsidx_path = os.path.join(docset_name, "Contents", "Resources", "docSet.dsidx")
    icon = os.path.join(docset_name, "icon.png")
    info = os.path.join(docset_name, "Contents", "Info.plist")
    metadata = os.path.join(docset_name, "meta.json")

    # destination directory
    destpath = results.path
    if destpath and destpath[-1] != os.sep:
        # add system file separator to path
        destpath = results.path + os.sep

    # path to generate files
    docset_path = destpath + doc_path
    sqlite_path = destpath + dsidx_path
    info_path = destpath + info
    icon_path = destpath + icon
    meta_path = destpath + metadata

    # copy docs files
    copy_docs(source_dir, docset_path)

    # database
    add_urls(sqlite_path, docset_path)

    if not results.index_page:
        index_page = INDEX_FILE
    else:
        index_page = results.index_page

    # create infoplist file
    add_infoplist(info_path, docset_name)

    #  generate meta.json metadata file

    # get the Docset version
    docset_version = float(results.version)
    # if a no version given for the Docset
    if not isinstance(docset_version, float) and docset_version < 0.0:
        logger.warning(f"{Fore.YELLOW}**Warning**: docset version must be a positive real numbers(Default version 0.0 will be provided){Style.RESET_ALL}")
        add_meta(metadata, results.name)
    # version given
    add_meta(metadata, results.name, docset_version)

    # get the icon argument
    icon_filename = results.filename
    if icon_filename:
        if icon_filename[-4:] == ".png" and os.path.isfile(icon_filename) and check_icon_size(icon_filename,16):
            try:
                # copy icon image
                shutil.copy(icon_filename, icon_path)
                # check if icon@2x.png exists and copy it.
                if os.path.exists('icon@2x.png') and check_icon_size("icon@2x.png",32):
                    # copy icon 2x image
                    shutil.copy('icon@2x.png', os.path.dirname(icon_path))

                print(f"{Fore.GREEN}Create the Icon for the Docset!{Style.RESET_ALL}")

            except Exception as e:
                logger.error(f"{Fore.RED}**Error**:  Copy Icon file failed...{Style.RESET_ALL}")
                logger.error(e)
                clear_trash()
                sys.exit(2)
        else:
            logger.error(f"{Fore.RED}**Error**:  Icon file should be a valid PNG image...{Style.RESET_ALL}")
            clear_trash()
            sys.exit(2)
    else:
        pass

    print(f"{Fore.GREEN}Generate Docset Successfully!{Style.RESET_ALL}")
