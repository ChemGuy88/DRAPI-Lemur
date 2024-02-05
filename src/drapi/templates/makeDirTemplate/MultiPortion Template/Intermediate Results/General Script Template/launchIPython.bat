@REM REMEMBER: Change the following, if applicable:
@REM 1. `condaEnvPrefix`
set condaEnvPrefix="C:\Users\herman\Anaconda3\envs\idr-bian2"
@REM h/t to https://stackoverflow.com/questions/33024344/how-do-i-start-cmd-exe-k-with-multiple-commands
@REM h/t to https://stackoverflow.com/questions/62992989/how-to-run-ipython-notebook-with-batch-file-on-windows-10
Title My Anaconda IPython Starter
color 08
@REM The below command does the following:
@REM - opens the anaconda environment located at `condaEnvPrefix`
@REM - clears the screen
@REM - starts ipython
cmd.exe /k "C:\Users\herman\Anaconda3\Scripts\activate.bat %condaEnvPrefix% & cls & ipython"
