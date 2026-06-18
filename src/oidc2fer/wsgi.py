import os

from satosa.wsgi import app as satosa_app
from whitenoise import WhiteNoise

# Serve static files from the satosa runtime directory's static sub-folder.
# When running via gunicorn the working directory is set to satosa/ (see
# docker/files/usr/local/etc/gunicorn/satosa.py), so "static" resolves there.
app = WhiteNoise(
    satosa_app, root=os.path.join(os.curdir, "static"), index_file="index.html"
)
