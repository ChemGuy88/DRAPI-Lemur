OMOP Data Pull Installation Instructions

Follow the instructions in this file to perform OMOP data pulls for your data request.

1. Go to the directory of your data request 
2. Download the "OMOP Portion Template" using the download button ![GitLab download button](README Images/glDownloadButton.png "GitLab Download Button") on GitLab. Then select the "Download this Directory" option.

![Download GitLab directory](README Images/glDownloadDirectory.png)

3. There are two main pre-requisites to running the OMOP data pull code:

  - Download DRAPI-Lemur
  - Add DRAPI-Lemur to `PYTHONPATH`

# Download DRAPI-Lemur

- Go to `C:\Users\YOUR_USER_NAME\Documents\GitHub`, where `YOUR_USER_NAME` is your user name on Windows.
- Clone [DRAPI-Lemur](https://gitlab.ahc.ufl.edu/herman/drapi-lemur) to your GitHub folder.
- Rename the folder from **drapi-lemur** to **drapi**.

For convenience, below are the Windows Command Prompt commands you can run.

```shell
cd %USERPROFILE%\Documents\GitHub
git clone https://gitlab.ahc.ufl.edu/herman/drapi-lemur
mv drapi-lemur drapi
```

You may need to replace `%USERPROFILE%` with your actual user name.

# Add DRAPI-Lemur to `PYTHONPATH`

Depending on how you use Python, you may modify your `PYTHONPATH` differently. One way to do it is to modify the environment variable using Anaconda's virtual environments. Below is a breakdown of the steps and the corresponding link to Anaconda's documentation.

- Create an Anaconda environment you will use for OMOP data pulls. [Anaconda Documentation](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands)
- Add environment variables to your anaconda environment. [Anaconda Documentation](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables)

In the batch file you create from the above instructions add the following line

```batch
set "PYTHONPATH=%USERPROFILE%\Documents\GitHub\drapi\code"
```
