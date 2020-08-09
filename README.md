# uniqueMudSource
Source code and 

## Getting started

### Choose an IDE<br>
Feel free to use any IDE. I am documenting Atom, IDLE and VSCode. Recommending Atom.<br>

### Atom<br>
<pre>
	+Linux Mac & Windows compatible<br>
	+Very robust IDE<br>
	+Many methods to customize with packages<br>
	+Allows you to open files from the server directly in the IDE<br>
 	-Somewhat difficult to setup
</pre>
Download Atom from: https://atom.io/<br>
You MAY need to create your own shortcut. If one does not appear atom is located in `C:\Users\YOURID\AppData\Local\atom\`<br>
Install: https://atom.io/packages/script<br>
Install: https://atom.io/packages/ide-python<br>
Install remote connection: https://atom.io/packages/remote-sync<br>
Optional, python auto complete: https://atom.io/packages/autocomplete-python, I suggest to not use kite when offered.<br>
Optional, Minimap: https://atom.io/packages/minimap<br>

#### configure remote sync in atom<br>
create a project. Right click the project folder, `remote sync` -> `configure`<br>
<b>CAUTION! On the steps below do not remove the `.remote-sync.json` from the `ignore Paths` that is a clear text file with your password in it</b><br>
host is: `mud.techknowledge.repair`<br> port `22`<br> target directory `/home/dave/muddev/mygame`<br> uder username click the box `password`<br> below `Watch automatically` check the boxes for `upLoadOnSave` and `Delete localfile/folder upon remote delete`<br>click `save`<br>
Right click your project folder, select `remote sync` and click `download folder`<br>

#### linter error running flake8, while running Atom
run command `python -m pip install flake8 fixed the issue` on your shell, works in windows also<br>
	
#### IDLE<br>
<pre>
	+very easy installation method<br>
	+very light weight<br>
	+Linux Mac & Windows compatible<br>
	+Good for someone starting out, who is considering contributing code<br>
	-Few "high end" features
</pre>
IDLE Installation<br>
Download and install python from: https://www.python.org/downloads/windows/<br>
IDLE is part of the python installation.<br>
	
#### vscode<br>
<pre>
	+Linux Mac & Windows compatible<br>
	+More robust IDE<br>
	+Fairlt light weight<br>
	+Good for person considering contributing heavily<br>
 	-Slightly difficult to setup
</pre>
vscode installation<br>
download and install python: https://www.python.org/downloads/windows/<br>
download and install vscode: https://code.visualstudio.com/download<br>
Install the python extension for vscode: https://marketplace.visualstudio.com/items?itemName=ms-python.python<br>
Restart VS Code<br>
When you run your first script or restart you will be prompted to install pylint, install it.<br>
To create a file, click `file -> new file`. Save the file by clicking `file -> save`. In the `save as type` field near the bottom choose python.<br>
vscode installation reference from: reference https://code.visualstudio.com/docs/languages/python<br>




### pycharm -incomplete<br>
download pycharm pro<br>
reference: https://medium.com/@jvision/remote-development-with-pycharm-d741287e07de<br>
Follow steps at: https://gist.github.com/rszeto/e47d89773c283fff685b0a886517eb6b<br>
interpreter is /home/dave/muddev/evenv/bin/python<br>
remote project is: /home/dave/muddev<br>
Following steps above results in getting stuck at a loading components screen.

## Connecting to server
Download and install Drive Maker: http://backupchain.com/en/drivemaker/<br>
When connecting for the first time:
At `server type` check the bullet for sftp.
The `site address` is mud.techknowledge.repair, prefacing with sftp://mud.techknowledge.repair will not work.
Fill in your id and password. All other settins should be acceptable as default.
