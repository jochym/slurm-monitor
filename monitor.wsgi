#import sys
#sys.path.insert(0, '//to/the/application')

import os
activate_this = os.path.abspath('./venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application