# README

This is the folder structure for the Anaconda environment batch scripts. 
```text
    env-name
    └── etc
        └── conda
            ├── activate.d
            │   └── convenience.bat or convenience.sh
            └── deactivate.d
                └── convenience.bat or convenience.sh
```
Note `env-name` is the name of the anaconda environment, and `convenience` can be any name for your convenience batch script. A useful template is below. 

```batch
@REM Set environment variables (Remember to unset variables in the deactivation script)
set "IPYTHONDIR=%CONDA_PREFIX%\etc\ipython"
set "HFA_UFADUID=herman"
set "HFA_UFADPWD=mypassword"
set "PYTHONPATH=%USERPROFILE%\Documents\GitHub\hermanCode\Code"
set "EMPTY_VAR="
```

For macOS, use shell scripts, with a different syntax.

```shell
# Set environment variables (Remember to unset variables in the deactivation script)
export IPYTHONDIR="$CONDA_PREFIX/etc/ipython"
export HFA_UFADUID="herman"
export HFA_UFADPWD="mypassword"
```