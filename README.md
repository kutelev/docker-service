# **BEFORE YOU START**

**WARNING: ALL THE INSTRUCTIONS FROM THE BELOW ARE FOR WINDOWS ONLY**

This manual describes how Docker Linux containers can be run on Windows without Docker Desktop.

# Prerequisites

## Mandatory prerequisites

1. Purge Docker Desktop if you have it installed.
2. Make sure that Hyper-V is disabled.
3. Install VirtualBox.
4. Install Vagrant.
5. Make sure that both VirtualBox and Vagrant are on `PATH`.
6. Make sure you have at least Python 3.6 installed with Python launcher (`py`).
7. Download `docker.exe` file from https://gitlab.com/kutelev/docker-cli-for-windows/-/jobs/artifacts/master/raw/docker.exe?job=build and put it to a location
   which is on `PATH`.
8. Download Docker Compose binary from https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Windows-x86_64.exe, rename it
   to `docker-compose.exe` and put it side by side with `docker.exe`.
9. Set `DOCKER_HOST` environment variable to `tcp://127.0.0.1:2375`.
10. Set `COMPOSE_CONVERT_WINDOWS_PATHS` environment variable to `1`. With this variable set `docker-compose` will automatically convert Windows paths to Linux
    paths, for instance `E:\work\project` to `/e/work/project`.

## Recommended prerequisites

1. Set `VAGRANT_EXPERIMENTAL` environment variable to `disks`,
   otherwise VM will have not big enough storage.
2. Invoke `vagrant plugin install vagrant-vbguest` command.
   Without doing this there will be no VirtualBox Guest Additions installed in VM, as result shared folders will not work.

## Optional prerequisites

1. If you want Vagrant to store its data at a custom location, set `VAGRANT_HOME` environment variable. An example: `VAGRANT_HOME=E:\work\.vagrant.d`.
2. If you want VirtualBox to store VMs at a custom location, set `Default Machine Folder`. An example: `E:\work\virtual-machines`.
   `Default Machine Folder` can be change via command line: `vboxmanage setproperty machinefolder E:\work\virtual-machines`.

# Prepare VM

1. Execute `py -3 configure.py --help`. Read help carefully.
2. Execute `py -3 configure.py` with required arguments. For instance:
   ```text
   py -3 configure.py --cpus 4 --memory 8192 --synced-folders E:\work
   ```
3. In order to prepare VM invoke the following command line: `vagrant up`.
   This command will automatically provision VM with Docker service installed inside.

# Usage

1. Make sure that previous prepared VM is running.
2. If you need ports from your containers to be automatically published run `py -3 forwarder.py`.
3. Use docker a usual way.

**Important notice:** binding of local folders is not that straight as with Docker Desktop:

1. Windows paths can not be used as is.
2. For instance, if you have `E:\work` shared with VM and want `E:\work\some_project` to be mounted to a container you need to
   add `-v /e/work/some_project:/some_directory` to a command line:

```shell
docker run --rm -it -v /e/work/some_project:/some_directory -w /some_directory ubuntu:20.04 bash
```

**Important notice:** `docker-compose` (if `COMPOSE_CONVERT_WINDOWS_PATHS` environment variable is set to `1`) converts Windows paths to Linux ones
automatically.
