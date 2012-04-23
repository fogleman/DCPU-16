import distutils
import os
import py2exe
import shutil
import sys

def run_py2exe():
    py2exe.__version__
    sys.argv.append('py2exe')
    distutils.core.setup(
        options = {"py2exe":{
            "compressed": True,
            "optimize": 1,
            "bundle_files": 1,
            "excludes": ['Tkconstants', 'Tkinter', 'tcl'],
            "dll_excludes": ['msvcp90.dll'],
        }},
        windows = [{
            "script": "main.py",
            "dest_base": "dcpu16",
            "icon_resources": [(1, "icons/icon.ico")],
            "other_resources": [(24, 1, MANIFEST)],
        }],
        zipfile=None,
    )

def copy_file(src):
    print 'Copying:', src
    dst = os.path.join('dist', src)
    try:
        os.makedirs(os.path.split(dst)[0])
    except Exception:
        pass
    shutil.copyfile(src, dst)

def copy_directory(src):
    for path, _, files in os.walk(src):
        if '.svn' in path:
            continue
        for filename in files:
            copy_file(os.path.join(path, filename))

def main():
    run_py2exe()
    copy_directory('Microsoft.VC90.CRT')
    copy_directory('programs')
    copy_file('_emulator.dll')

MANIFEST = '''
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
  <assemblyIdentity
    version="2.0.0.0"
    processorArchitecture="x86"
    name="Star Rocket Level Editor"
    type="win32"
  />
  <description>Star Rocket Level Editor 1.0</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
          level="asInvoker"
          uiAccess="false"
        />
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.VC90.CRT"
        version="9.0.21022.8"
        processorArchitecture="x86"
        publicKeyToken="1fc8b3b9a1e18e3b"
      />
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="x86"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
</assembly>
'''

if __name__ == '__main__':
    main()
