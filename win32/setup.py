from distutils.core import setup
import py2exe

opts = {
    'py2exe': {
        'compressed': 1,
        'optimize': 2,
       'bundle_files': 1
    }
}

setup(windows=['trimps.py'], options=opts)
