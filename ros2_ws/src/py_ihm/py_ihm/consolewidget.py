#! /usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()   # noqa

import gevent
import sys

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication
from pyqtconsole.console import PythonConsole
import pyqtconsole.highlighter as hl


def define_format():
	new_format ={
    'keyword':    hl.format('blue', 'bold'),
    'operator':   hl.format('red'),
    'brace':      hl.format('darkGray'),
    'defclass':   hl.format('black', 'bold'),
    'string':     hl.format('magenta'),
    'string2':    hl.format('darkMagenta'),
    'comment':    hl.format('darkGreen', 'italic'),
    'self':       hl.format('black', 'italic'),
    'numbers':    hl.format('brown'),
    'inprompt':   hl.format('darkBlue', 'bold'),
    'outprompt':  hl.format('darkRed', 'bold'),
	}
	return new_format
#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from qtpy.QtWidgets import QApplication
from pyqtconsole.console import PythonConsole


def greet():
    print("hello world")


if __name__ == '__main__':
    app = QApplication([])

    console = PythonConsole(formats =define_format())
    print(type(console))
    console.push_local_ns('greet', greet)
    console.show()
    console.eval_in_thread()
    sys.exit(app.exec_())

