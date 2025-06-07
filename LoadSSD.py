#!/usr/bin/env python3

# This script moves files placed in the "SHARE_PATHS" locations to the
# "RAW_FOLDER" locations under FOOTAGE_PATH and FOOTAGE_FOLDERS for all
# cars in CAR_LIST. I use it to pick up files placed in a CIFS share by
# teslausb and move them to a location for merging and viewing.
# Enhanced to copy event.mp4 files

import os
import time
import shutil
import re
import json
import TCMConstants
import datetime

logger = TCMConstants.get_logger()

def main():
    if len(TCMConstants.SHARE_PATHS) <= 0:
            logger.error("No share paths defined, please fix in TCMConstants.py and restart.")
            TCMConstants.exit_gracefully(TCMConstants.SPECIAL_EXIT_CODE, None)
    if not have_required_permissions():
            logger.error("Missing some required permissions, exiting")
            TCMConstants.exit_gracefully(TCMConstants.SPECIAL_EXIT_CODE, None)

    while True:
            for index, share in enumerate(TCMConstants.SHARE_PATHS):
                    for folder in TCMConstants.FOOTAGE_FOLDERS:
                            for root, dirs, files in os.walk(f"{share}{folder}", topdown=False):
                                    logger.debug(f"Checking share path: {share}{folder}")
                                    logger.debug(f"Files in {root}: {files}")
                                    for name in files:
                                            if file_has_proper_name(name):
                                                    sub_path = folder
                                                    if TCMConstants.MULTI_CAR:
                                                            sub_path = f"{TCMConstants.CAR_LIST[index]}/{folder}"
                                                    move_file(os.path.join(root, name), sub_path, name, root)
                                            elif name != "thumb.png":
                                                    logger.warning(f"File '{name}' has invalid name, skipping")

            time.sleep(TCMConstants.SLEEP_DURATION)

### Startup functions ###

def have_required_permissions():
        have_perms = True
        for index, share in enumerate(TCMConstants.SHARE_PATHS):
                for folder in TCMConstants.FOOTAGE_FOLDERS:
                        have_perms = have_perms and TCMConstants.check_permissions(f"{share}{folder}", True)
                        sub_path = folder
                        if TCMConstants.MULTI_CAR:
                                sub_path = f"{TCMConstants.CAR_LIST[index]}/{folder}"
                        have_perms = have_perms and TCMConstants.check_permissions(
                                f"{TCMConstants.FOOTAGE_PATH}{sub_path}/{TCMConstants.RAW_FOLDER}", True)
                        have_perms = have_perms and TCMConstants.check_permissions(
                                f"{TCMConstants.FOOTAGE_PATH}{sub_path}/{TCMConstants.FULL_FOLDER}", True)
        return have_perms

### Loop functions ###

def move_file(file, folder, name, root):
        target_name = name
        if name == "event.mp4":
                # Attempt to get timestamp from folder name or fallback to file time
                folder_timestamp = os.path.basename(root)
                try:
                        datetime.datetime.strptime(folder_timestamp, TCMConstants.FILENAME_TIMESTAMP_FORMAT)
                except:
                        ts = datetime.datetime.fromtimestamp(os.path.getmtime(file))
                        folder_timestamp = ts.strftime(TCMConstants.FILENAME_TIMESTAMP_FORMAT)
                target_name = f"{folder_timestamp}-front.mp4"

        dest_raw = f"{TCMConstants.FOOTAGE_PATH}{folder}/{TCMConstants.RAW_FOLDER}/{target_name}"
        dest_full = f"{TCMConstants.FOOTAGE_PATH}{folder}/{TCMConstants.FULL_FOLDER}/{folder_timestamp}-full.mp4" if name == "event.mp4" else None

        if TCMConstants.check_file_for_read(dest_raw):
                logger.debug(f"Destination file already exists at: {dest_raw}")
        else:
                logger.info(f"Moving file {file} into {folder} as {target_name}")
                if TCMConstants.check_file_for_read(file):
                        try:
                                shutil.move(file, dest_raw)
                                logger.debug(f"Moved file {file} to {dest_raw}")
                                # Copy to FULL folder as-is for event.mp4
                                if dest_full:
                                        shutil.copyfile(dest_raw, dest_full)
                                        logger.debug(f"Copied single-camera clip to {dest_full}")
                        except Exception as e:
                                logger.error(f"Failed to move {file} to {dest_raw}: {e}")
                else:
                        logger.debug(f"File {file} still being written, skipping for now")

def file_has_proper_name(file):
        return (
                file == TCMConstants.EVENT_JSON or
                file == "event.mp4" or
                TCMConstants.FILENAME_PATTERN.match(file)
        )

if __name__ == '__main__':
        main()
