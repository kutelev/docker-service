import argparse
import os
import psutil
import sys


def convert_windows_path_to_linux_path(windows_path: str) -> str:
    drive, path = windows_path.split(':')
    drive, path = drive.lower(), path.replace('\\', '/').strip('/')
    return f'/{drive}/{path}'


def main() -> int:
    current_directory_path = os.path.abspath(os.path.dirname(os.path.relpath(__file__)))

    default_cpu_count = psutil.cpu_count(logical=False)
    total_memory_size = psutil.virtual_memory().total // 1024 // 1024
    default_memory_size = max(total_memory_size // 4, 16 * 1024)

    home_path = f'''{os.environ['HOMEDRIVE']}{os.environ['HOMEPATH']}'''.replace('\\\\', '\\')
    synced_folders = {home_path: convert_windows_path_to_linux_path(home_path)}

    arg_parser = argparse.ArgumentParser(description='Preconfigure Vagrantfile')
    arg_parser.add_argument(
        '--cpus', type=int, required=False, default=default_cpu_count,
        help=f'CPU count to give to VM to, this number must never exceed physical CPU count. Default: {default_cpu_count}'
    )
    arg_parser.add_argument(
        '--memory', type=int, required=False, default=default_memory_size,
        help=f'Memory size in GiB to assign to VM to. Default: {default_memory_size}'
    )
    arg_parser.add_argument(
        '--synced-folders', type=str, required=False, default=[], nargs='+',
        help='List of directories on the host system to share with VM, these directories can be later shared with Docker containers. '
             f'Home directory ({home_path}) is shared as "{synced_folders[home_path]}" by default. Example: --synced-folders E:\\projects Z:\\streams'
    )
    args = arg_parser.parse_args()

    # Write template Vagrantfile.
    with open(os.path.join(current_directory_path, 'Vagrantfile.template'), 'r') as f:
        vagrant_file = f.read()

    # Set CPU count and memory size.
    vagrant_file = vagrant_file.format(cpus=args.cpus, memory=args.memory)

    # Configure synced folders.
    vagrant_file = vagrant_file.rstrip().split('\n')
    vagrant_file = [line.rstrip('') for line in vagrant_file]
    for windows_path in args.synced_folders:
        synced_folders[windows_path] = convert_windows_path_to_linux_path(windows_path)
    begin = vagrant_file.index('  # BEGIN OF SYNCED FOLDERS') + 1
    for index, (windows_path, linux_path) in enumerate(synced_folders.items()):
        windows_path = windows_path.replace('\\', '\\\\')
        vagrant_file.insert(begin + index, f'''  config.vm.synced_folder "{windows_path}", "{linux_path}"''')
    vagrant_file = '\n'.join(vagrant_file) + '\n'

    # Write configured Vagrantfile back.
    with open(os.path.join(current_directory_path, 'Vagrantfile'), 'w') as f:
        f.write(vagrant_file)

    return 0


if __name__ == '__main__':
    sys.exit(main())
