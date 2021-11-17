## Installation

```
pip3 install --user pyqt5  
sudo apt-get install python3-pyqt5  
sudo apt-get install pyqt5-dev-tools
sudo apt-get install qttools5-dev-tools
```
____
## Configuring to run from terminal

`$ qtchooser -run-tool=designer -qt=5`

**OR**

Write the following in `/usr/lib/x86_64-linux-gnu/qt-default/qtchooser/default.conf`

```
/usr/lib/x86_64-linux-gnu/qt5/bin
/usr/lib/x86_64-linux-gnu
```
____
## Code Generation

**Create uic.py file.**

```
#!/usr/bin/python3

import subprocess
import sys

child = subprocess.Popen(['pyuic5' ,'-x',sys.argv[1]],stdout=subprocess.PIPE)

print(str(child.communicate()[0],encoding='utf-8'))
```

`$ chmod +x uic.py`

**Create a symlink:**

`$ sudo ln uic.py "/usr/lib/x86_64-linux-gnu/qt5/bin/uic"`

____

## Desktop Entry

```
[Desktop Entry]
Name=Qt5 Designer
Icon=designer
Exec=/usr/lib/x86_64-linux-gnu/qt5/bin/designer
Type=Application
Categories=Application
Terminal=false
StartupNotify=true
Actions=NewWindow

Name[en_US]=Qt5 Designer

[Desktop Action NewWindow]
Name=Open a New Window
Exec=/usr/lib/x86_64-linux-gnu/qt5/bin/designer
```

**save in ~/.local/share/application with .desktop extension**