#!/usr/bin/env python3


"""copy the HTML,CSS,JS files into docs folder.

        Args:
            dir_source(str): the source folder of the website.
            docs_dir(str): the destination docs folder.
"""

import os
import shutil
import logging
from colorama import Fore, Style
import colorama
from tqdm import tqdm

dir_source = "HDL-Docs"
docs_dir = "docs"
    
exists = os.path.exists(dir_source)
    
if not exists:
    print(f"{Fore.RED}Not HDL-Docs Folder found!{Style.RESET_ALL}")
    raise Exception(f"{Fore.RED}**Error**: Not HDL-Docs Folder found! {Style.RESET_ALL}")       

print(f"{Fore.GREEN}Copying the HDL-Docs Folder into docs!{Style.RESET_ALL}")
for subdir in tqdm(os.listdir(dir_source)):
    # skip vscode folder
    if '.vscode' in subdir:
        continue
    try:
            shutil.copytree(os.path.join(dir_source, subdir), os.path.join(docs_dir, subdir), dirs_exist_ok=True )
    except NotADirectoryError as not_dir:
            try:
                    shutil.copy(os.path.join(dir_source, subdir), os.path.join(docs_dir, subdir))
            except:
                    logging.error(f"{Fore.RED}{e}{Style.RESET_ALL}")
                    raise Exception(f"{Fore.RED}**Error**:  Copying Html Documents Failed...{Style.RESET_ALL}") from not_dir

