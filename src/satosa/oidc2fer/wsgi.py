import os

from satosa.wsgi import app as satosa_app
from whitenoise import WhiteNoise

# Wrap the SATOSA WSGI app in WhiteNoise to serve static files
app = WhiteNoise(
    satosa_app, root=os.path.join(os.curdir, "static"), index_file="index.html"
)
