import sys
sys.setrecursionlimit(5000)

import os
import site
import glob
import scipy
import matplotlib
from cx_Freeze import setup, Executable

siteDir = site.getsitepackages()[1]
includeDllPath = os.path.join(siteDir, "gnome")

# This is the list of dll which are required by PyGI.
# I get this list of DLL using http://technet.microsoft.com/en-us/sysinternals/bb896656.aspx
#   Procedure: 
#    1) Run your from from your IDE
#    2) Command for using listdlls.exe
#        c:/path/to/listdlls.exe python.exe > output.txt
#    3) This would return lists of all dll required by you program 
#       in my case most of dll file were located in c:\python27\Lib\site-packages\gnome 
#       (I am using PyGI (all in one) installer)
#    4) Below is the list of gnome dll I recevied from listdlls.exe result. 

# If you prefer you can import all dlls from c:\python27\Lib\site-packages\gnome folder
missingDLL = glob.glob(includeDllPath + "\\" + '*.dll')
#print(missingDLL)
# List of dll I recevied from listdlls.exe result
#missingDLL = ['libffi-6.dll',
#              'libglib-2.0-0.dll',
#              'libgob]ject-2.0-0.dll',
#              'libgirepository-1.0-1.dll',
#              'libgio-2.0-0.dll',
#              'libgmodule-2.0-0.dll',
#              'libintl-8.dll',
#              'libzzz.dll',
#              'libwinpthread-1.dll',
#              'libgtk-3-0.dll',
#              'libatk-1.0-0.dll',
#              'libcairo-gobject-2.dll',
#              'libepoxy-0.dll',
#              'libgdk_pixbuf-2.0-0.dll',
#              'libpango-1.0-0.dll',
#              'libpangocairo-1.0-0.dll',
#              'libpangowin32-1.0-0.dll',
#              'libfontconfig-1.dll',
#              'libfreetype-6.dll',
#              'libpng16-16.dll',
#              'libjasper-1.dll',
#              'libjpeg-8.dll',
#              'librsvg-2-2.dll',
#              'libtiff-5.dll',
#              'libpangoft2-1.0-0.dll',
#              'libwebp-5.dll',
#              'libxmlxpat.dll',
#              'libharfbuzz-0.dll'
#              ]


includeFiles = []
for DLL in missingDLL:
    #includeFiles.append((os.path.join(includeDllPath, DLL), DLL))
    includeFiles.append(DLL) 

# You can import all Gtk Runtime data from gtk folder              
gtkLibs= ['etc','lib','share']

# You can import only important Gtk Runtime data from gtk folder  
#gtkLibs = ['lib\\gdk-pixbuf-2.0',
#           'lib\\girepository-1.0',
#           'share\\glib-2.0',
#           'lib\\gtk-3.0']



for lib in gtkLibs:
    includeFiles.append((os.path.join(includeDllPath, lib), lib))


#Matplotlib
includeFiles.append((matplotlib.get_data_path(), "mpl-data"))

includeFiles.append("interface1.glade")
includeFiles.append("config.ini")
#SciPy
scipy_path = os.path.dirname(scipy.__file__)
includeFiles.append(scipy_path)

	
base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "PyGI Example",
    version = "1.0",
    description = "PyGI Example",
    options = {'build_exe' : {
        'compressed': False,
        'includes': ["gi", "matplotlib.backends.backend_tkagg", "FileDialog"],
        'excludes': ['wx', 'pydoc_data', 'curses', 'collections.abc'],
        'packages': ["gi"],
        'include_files': includeFiles
    }},
    executables = [
        Executable("Controller.py",
                   base=base
                   )
    ]
)
