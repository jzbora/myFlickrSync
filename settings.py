import os.path
import sys
from sys import platform

def cur_file_dir():
    sys_path = sys.path[0]
    if os.path.isdir(sys_path):
        return sys_path
    elif os.path.isfile(sys_path):
        return os.path.dirname(sys_path)

if platform == 'win32':        
    import winpaths
    path = winpaths.get_common_appdata()
    path = os.path.join(path, 'mySync')
    if not os.path.isdir(path): os.mkdir(path)
elif platform == 'darwin':
    user_path = os.path.expanduser('~') 
    path = os.path.join(user_path, 'Library')
    if not os.path.isdir(path): os.mkdir(path)
    path = os.path.join(path, 'Application Support')
    if not os.path.isdir(path): os.mkdir(path)
    path = os.path.join(path, 'mySync')
    if not os.path.isdir(path): os.mkdir(path)
else:
    path = cur_file_dir()

LOG_PATH = path
DATA_PATH = os.path.join(path, 'data')
AUTH_PATH = os.path.join(path, 'auth')

MAIN_VERSION = '1.0.0'
VERSION = '20130531'

UPLOAD_URL = "http://api.flickr.com/services/upload/"

RESTART_CODE = 1000

ERROR_CHECK_SECOND = 600

SUPPORT_FORMATS = ('.jpg', '.png')

FLICKR_APP_KEY = "input your flickr app key"
FLICKR_APP_SECRET = "input your flickr app secret"

try:
    from local_settings import *
except ImportError:
    pass
