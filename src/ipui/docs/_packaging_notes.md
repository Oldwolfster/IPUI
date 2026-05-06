# packaging notes.

## How to check for __inits
>  from root directory run

```bash
$dirs = @(
    "src\ipui\engine",
    "src\ipui\widgets",
    "src\ipui\utils",
    "src\ipui\_forms",
    "src\ipui\_forms\NeuroForge",
    "src\ipui\_forms\NeuroForge\custom_widgets",
    "src\ipui\_forms\Showcase"
)
foreach ($d in $dirs) {
    if (Test-Path "$d\__init__.py") { Write-Host "OK   $d" }
    else                            { Write-Host "MISS $d" }
}
```

## one time install 

pip install build twine


## to build wheel
python -m build
should get 
Successfully built ipui-0.1.0.tar.gz and ipui-0.1.0-py3-none-any.whl


## validate

```bash
python -m zipfile -l dist/ipui-0.1.0-py3-none-any.whl
```

## To rebuild wheel  

### - in PyCharm term - from ROOT of project
Remove-Item -Recurse -Force dist, build, src\ipui.egg-info -ErrorAction SilentlyContinue
python -m build

### Back in cmd window
pip install --force-reinstall C:\SynologyDrive\Development\PyCharm\IdiotProofUIV3\dist\ipui-0.1.0-py3-none-any.whl

python smoke.py
   
if need to reactivate venv
testenv\Scripts\activate.bat


## Setup a venv to test
### Create folder and venv
cd C:\
mkdir ipui-test
cd ipui-test
python -m venv testenv

### Activate venv
testenv\Scripts\activate.bat
> Your prompt should now change to show (testenv) at the front, like

### check pip
pip list 

### Install wheel
pip install C:\SynologyDrive\Development\PyCharm\IdiotProofUIV3\dist\ipui-0.1.0-py3-none-any.whl

### check pip - should now show pygame-ce and ipui
pip list 



## Test app
notepad smoke.py

> add code

python smoke.py



