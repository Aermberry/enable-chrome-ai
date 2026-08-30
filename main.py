import json
import os
import subprocess
import sys
import tempfile
import time

import psutil


def get_version_and_user_data_path():
    os_and_user_data_paths = {
        'win32': {
            'stable': '~/AppData/Local/Google/Chrome/User Data',
            'canary': '~/AppData/Local/Google/Chrome SxS/User Data',
            'dev': '~/AppData/Local/Google/Chrome Dev/User Data',
            'beta': '~/AppData/Local/Google/Chrome Beta/User Data',
        },
        'linux': {
            'stable': '~/.config/google-chrome',
            'canary': '~/.config/google-chrome-canary',
            'dev': '~/.config/google-chrome-unstable',
            'beta': '~/.config/google-chrome-beta',
        },
        'darwin': {
            'stable': '~/Library/Application Support/Google/Chrome',
            'canary': '~/Library/Application Support/Google/Chrome Canary',
            'dev': '~/Library/Application Support/Google/Chrome Dev',
            'beta': '~/Library/Application Support/Google/Chrome Beta',
        },
    }

    for platform, version_and_user_data_path in os_and_user_data_paths.items():
        if sys.platform.startswith(platform):
            return {
                version: path
                for version, user_data_path in version_and_user_data_path.items()
                if os.path.exists(path := os.path.abspath(os.path.expanduser(user_data_path)))
            }
    raise RuntimeError(f'Unsupported platform {sys.platform}')


def is_chrome_process(process):
    """Return whether *process* belongs to a Chrome executable."""
    try:
        name = process.info.get('name') or process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
    if sys.platform == 'darwin':
        return (name or '').startswith('Google Chrome')
    return os.path.splitext(name or '')[0].lower() == 'chrome'


def shutdown_chrome(timeout=10):
    """Stop every Chrome process and wait for its Local State writer to exit."""
    processes = [
        process for process in psutil.process_iter(attrs=['name', 'exe'])
        if is_chrome_process(process)
    ]
    executables = set()
    for process in processes:
        try:
            location = process.info.get('exe') or process.exe()
            if location:
                executables.add(location)
            process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    _, alive = psutil.wait_procs(processes, timeout=timeout)
    for process in alive:
        try:
            process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    _, still_alive = psutil.wait_procs(alive, timeout=timeout)
    if still_alive:
        pids = ', '.join(str(process.pid) for process in still_alive)
        raise RuntimeError(f'Chrome processes did not exit: {pids}')
    return executables


def get_last_version(user_data_path):
    last_version_file = os.path.join(user_data_path, 'Last Version')
    if not os.path.exists(last_version_file):
        return None
    with open(last_version_file, 'r', encoding='utf-8') as file:
        return file.read().strip() or None


def set_glic_eligibility(local_state):
    """Mark every local Chrome profile as GLIC-eligible.

    Chrome stores this value in profile.info_cache.<profile>, rather than in
    the top-level ``glic`` preference. Newer Chrome builds may omit the key,
    so it must be created instead of only changing an existing key.
    """
    profile = local_state.setdefault('profile', {})
    if not isinstance(profile, dict):
        raise ValueError('Local State has an invalid profile section')
    info_cache = profile.setdefault('info_cache', {})
    if not isinstance(info_cache, dict):
        raise ValueError('Local State has an invalid profile.info_cache section')

    modified = False
    for profile_name, profile_info in info_cache.items():
        if not isinstance(profile_info, dict):
            continue
        if profile_info.get('is_glic_eligible') is not True:
            profile_info['is_glic_eligible'] = True
            modified = True
            print(f'Patched is_glic_eligible for profile {profile_name}')
    return modified


def atomic_write_json(path, data):
    directory = os.path.dirname(path)
    file_descriptor, temporary_path = tempfile.mkstemp(
        prefix='Local State.', suffix='.tmp', dir=directory, text=True
    )
    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, separators=(',', ':'))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


def patch_local_state(user_data_path, last_version):
    local_state_file = os.path.join(user_data_path, 'Local State')
    if not os.path.exists(local_state_file):
        print('Failed to patch Local State. File not found', local_state_file)
        return False

    with open(local_state_file, 'r', encoding='utf-8') as file:
        local_state = json.load(file)

    modified = set_glic_eligibility(local_state)
    if local_state.get('variations_country') != 'us':
        local_state['variations_country'] = 'us'
        modified = True
        print('Patched variations_country')

    expected_consistency_country = [last_version, 'us']
    if local_state.get('variations_permanent_consistency_country') != expected_consistency_country:
        local_state['variations_permanent_consistency_country'] = expected_consistency_country
        modified = True
        print('Patched variations_permanent_consistency_country')

    # This controls whether Chrome displays the GLIC entry point. It is
    # separate from the per-profile eligibility cache above.
    glic = local_state.setdefault('glic', {})
    if isinstance(glic, dict) and glic.get('launcher_enabled') is not True:
        glic['launcher_enabled'] = True
        modified = True
        print('Patched glic.launcher_enabled')

    if modified:
        atomic_write_json(local_state_file, local_state)
        print('Succeeded in patching Local State')
    else:
        print('Local State already contains the requested local settings')
    return modified


def main():
    version_and_user_data_path = get_version_and_user_data_path()
    if not version_and_user_data_path:
        raise RuntimeError('No available user data path found')

    terminated_chromes = shutdown_chrome()
    if terminated_chromes:
        print('Shutdown Chrome and waited for all processes to exit')

    for version, user_data_path in version_and_user_data_path.items():
        last_version = get_last_version(user_data_path)
        if last_version is None:
            print('Failed to get version. File not found', os.path.join(user_data_path, 'Last Version'))
            continue
        print(f'Patching Chrome {version} {last_version} "{user_data_path}"')
        patch_local_state(user_data_path, last_version)

    if terminated_chromes:
        print('Restart Chrome')
        for chrome in terminated_chromes:
            subprocess.Popen([chrome], stderr=subprocess.DEVNULL)
            time.sleep(0.2)

    print(
        'Local eligibility has been updated. Availability is still verified by '
        'Google using the signed-in account, device language, and network region.'
    )
    try:
        if sys.stdin.isatty():
            input('Enter to continue...')
    except EOFError:
        pass


if __name__ == '__main__':
    main()
