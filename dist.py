# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2018 McAfee LLC - All Rights Reserved.
################################################################################

from __future__ import absolute_import
from __future__ import print_function
import re
import os
import subprocess
import sys
from tempfile import mkstemp
from shutil import copyfile, copytree, make_archive, move, rmtree


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    os.close(fh)
    # Remove original file
    os.remove(file_path)
    # Move new file
    move(abs_path, file_path)

print("Starting dist.\n")

VERSION = __import__('dxlbootstrap').get_version()
RELEASE_NAME = "dxlbootstrap-python-dist-" + str(VERSION)

DIST_PY_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))
DIST_DIRECTORY = os.path.join(DIST_PY_FILE_LOCATION, "dist")
DIST_DOCTMP_DIR = os.path.join(DIST_DIRECTORY, "doctmp")
SETUP_PY = os.path.join(DIST_PY_FILE_LOCATION, "setup.py")
DIST_LIB_DIRECTORY = os.path.join(DIST_DIRECTORY, "lib")
DIST_RELEASE_DIR = os.path.join(DIST_DIRECTORY, RELEASE_NAME)

# Remove the dist directory if it exists
if os.path.exists(DIST_DIRECTORY):
    print("\nRemoving dist directory: " + DIST_DIRECTORY + "\n")
    rmtree(DIST_DIRECTORY)

# Make the dist directory
print("\nMaking dist directory: " + DIST_DIRECTORY + "\n")
os.makedirs(DIST_DIRECTORY)

# Call Sphinx to create API doc
print("\nCalling sphinx-apidoc\n")
subprocess.check_call(["sphinx-apidoc",
                       "--force",
                       "--separate",
                       "--no-toc",
                       "--output-dir=" + DIST_DOCTMP_DIR,
                       os.path.join(DIST_PY_FILE_LOCATION, "dxlbootstrap")])

# Delete generate files
for f in os.listdir(DIST_DOCTMP_DIR):
    if re.search("dxlbootstrap.generate.*", f):
        os.remove(os.path.join(DIST_DOCTMP_DIR, f))

# Copy files to dist/doctmp
print("\nCopying conf.py, docutils.conf, and sdk directory\n")
copyfile(os.path.join(DIST_PY_FILE_LOCATION, "doc", "conf.py"),
         os.path.join(DIST_DOCTMP_DIR, "conf.py"))
copyfile(os.path.join(DIST_PY_FILE_LOCATION, "doc", "docutils.conf"),
         os.path.join(DIST_DOCTMP_DIR, "docutils.conf"))
copytree(os.path.join(DIST_PY_FILE_LOCATION, "doc", "sdk"), DIST_DOCTMP_DIR,
         dirs_exist_ok=True)

# Call Sphinx build
print("\nCalling sphinx-build\n")
subprocess.check_call(["sphinx-build", "-b", "html", DIST_DOCTMP_DIR, os.path.join(DIST_DIRECTORY, "doc")])

replace(os.path.join(DIST_DIRECTORY, "doc", "_static", "classic.css"), "text-align: justify", "text-align: none")

# Delete .doctrees
rmtree(os.path.join(os.path.join(DIST_DIRECTORY, "doc"), ".doctrees"))
# Delete .buildinfo
os.remove(os.path.join(os.path.join(DIST_DIRECTORY, "doc"), ".buildinfo"))

# Move README.html to root of dist directory
print("\nMoving README.html\n")
move(os.path.join(DIST_DOCTMP_DIR, "README.html"), DIST_DIRECTORY)

# Remove doctmp directory
print("\nDeleting doctmp directory\n")
rmtree(DIST_DOCTMP_DIR)

# Call setup.py
print("\nRunning setup.py sdist\n")
subprocess.check_call([sys.executable,
                       SETUP_PY,
                       "sdist",
                       "--format",
                       "zip",
                       "--dist-dir",
                       DIST_LIB_DIRECTORY])

print("\nRunning setup.py bdist_wheel\n")
subprocess.check_call([sys.executable,
                       SETUP_PY,
                       "bdist_wheel",
                       "--dist-dir",
                       DIST_LIB_DIRECTORY,
                       "--universal"])

# cp -rf config dist
print("\nCopying config in to dist directory\n")
copytree(os.path.join(DIST_PY_FILE_LOCATION, "config"),
         os.path.join(DIST_DIRECTORY, "config"),
         dirs_exist_ok=True)

# Copy everything in to release dir
print("\nCopying dist to " + DIST_RELEASE_DIR + "\n")
copytree(DIST_DIRECTORY, DIST_RELEASE_DIR, dirs_exist_ok=True)

# rm -rf build
print("\nRemoving build directory\n")
rmtree(os.path.join(DIST_PY_FILE_LOCATION, "build"))

# rm -rf dxlbootstrap.egg-info
print("\nRemoving dxlbootstrap.egg-info\n")
rmtree(os.path.join(DIST_PY_FILE_LOCATION, "dxlbootstrap.egg-info"))

# Make dist zip
print("\nMaking dist zip\n")
make_archive(DIST_RELEASE_DIR, "zip", DIST_DIRECTORY, RELEASE_NAME)

print("\nRemoving " + DIST_RELEASE_DIR + "\n")
rmtree(DIST_RELEASE_DIR)

print("\nFinished")
