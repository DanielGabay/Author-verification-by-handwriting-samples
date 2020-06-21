# import pkg_resources.py2_warn # import just as workaround for pyinstaller error
import eel
from main import _gui_entry

eel.init('GUI')
@eel.expose
def gui_entry(path1, path2):
	output = _gui_entry(path1, path2)
	return output

eel.start('index.html', size=(1000, 600))
