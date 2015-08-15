from distutils.core import setup
import py2exe
#setup(windows=["Snake.py"])
#setup(console=['Snake.pyw'])
setup(
    windows = [
        {
            "script": "Snake.py",
            "icon_resources": [(1, "snakeicon.ico")]
        }
    ],
)