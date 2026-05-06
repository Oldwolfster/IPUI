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