import sys
sys.setrecursionlimit(5000)

import matplotlib

#import os
#import site


#from os import listdir
#from os.path import isfile, join
#typelib_path = os.path.join(site.getsitepackages()[1], 'gnome', 'lib', 'girepository-1.0')

#print([f for f in listdir(typelib_path) if isfile(join(typelib_path, f))])

#from distutils.core import setup
#from os.path import dirname
#import py2exe

#includefiles = matplotlib.get_py2exe_datafiles()
#print(includefiles)
# import lib2to3
# lib23_path = dirname(lib2to3.__file__)
# includefiles.append(lib23_path)

opts = {
    "py2exe": {
		"includes" : ["gi", "matplotlib.backends.backend_qt4agg", "scipy.sparse.csgraph._validation"],
		"packages": ["gi"],
		"dll_excludes": ["MSVCP90.dll","libzmq.pyd","geos_c.dll","api-ms-win-core-string-l1-1-0.dll","api-ms-win-core-registry-l1-1-0.dll","api-ms-win-core-errorhandling-l1-1-1.dll","api-ms-win-core-string-l2-1-0.dll","api-ms-win-core-profile-l1-1-0.dll","api-ms-win*.dll","api-ms-win-core-processthreads-l1-1-2.dll","api-ms-win-core-libraryloader-l1-2-1.dll","api-ms-win-core-file-l1-2-1.dll","api-ms-win-security-base-l1-2-0.dll","api-ms-win-eventing-provider-l1-1-0.dll","api-ms-win-core-heap-l2-1-0.dll","api-ms-win-core-libraryloader-l1-2-0.dll","api-ms-win-core-localization-l1-2-1.dll","api-ms-win-core-sysinfo-l1-2-1.dll","api-ms-win-core-synch-l1-2-0.dll","api-ms-win-core-heap-l1-2-0.dll","api-ms-win-core-handle-l1-1-0.dll","api-ms-win-core-io-l1-1-1.dll","api-ms-win-core-com-l1-1-1.dll","api-ms-win-core-memory-l1-1-2.dll","api-ms-win-core-version-l1-1-1.dll","api-ms-win-core-version-l1-1-0.dll"],
        "excludes": ["tkinter", "lib2to3"]
#		"dist_dir": "bin"
    }
}
#setup(data_files=includefiles, options=opts, console=['Controller.py'])


from distutils.core import setup
import py2exe
import sys, os, site, shutil

includefiles = matplotlib.get_py2exe_datafiles()

site_dir = site.getsitepackages()[1]
include_dll_path = os.path.join(site_dir, "gnome")

gtk_dirs_to_include = ['etc', 'lib\\gtk-3.0', 'lib\\girepository-1.0', 'lib\\gio', 'lib\\gdk-pixbuf-2.0', 'share\\glib-2.0', 'share\\fonts', 'share\\icons', 'share\\themes\\Default', 'share\\themes\\HighContrast']

gtk_dlls = []
tmp_dlls = []
cdir = os.getcwd()
for dll in os.listdir(include_dll_path):
    if dll.lower().endswith('.dll'):
        gtk_dlls.append(os.path.join(include_dll_path, dll))
        tmp_dlls.append(os.path.join(cdir, dll))

for dll in gtk_dlls:
    shutil.copy(dll, cdir)

# -- change main.py if needed -- #
setup(console=['test_basic_gtk.py'], data_files=includefiles, options=opts) 

dest_dir = os.path.join(cdir, 'dist')

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

for dll in tmp_dlls:
    shutil.copy(dll, dest_dir)
    os.remove(dll)

for d  in gtk_dirs_to_include:
    shutil.copytree(os.path.join(site_dir, "gnome", d), os.path.join(dest_dir, d))
