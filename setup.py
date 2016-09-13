from distutils.core import setup
import py2exe
import sys
sys.argv.append('py2exe')
setup(console=[{'script': 'electsys_assistance.py', 'includes': ['splinter.browser', 'PIL.Image', 'pytesseract']}])
