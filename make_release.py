#!/usr/bin/env python

"""Release script to publish release module to pipy."""

import io
import os
import sys

VERSION_FILE_PATH = os.path.join(os.path.dirname('__file__'), 'my_django_tweaks', '__init__.py')
CHANGELOG_PATH = os.path.join(os.path.dirname('__file__'), 'CHANGELOG.rst')

MESSAGE_RED = '\033[1;31m{}\033[0m'
MESSAGE_GREEN = '\033[1;32m{}\033[0m'
MESSAGE_YELLOW = '\033[1;33m{}\033[0m'


def get_current_version():
    # current = io.open(VERSION_FILE_PATH, encoding='utf-8').read().rstrip()
    with open(VERSION_FILE_PATH, 'rt') as f:
        for line in f:
            if line.startswith('__version__ '):
                current = line.split('=')[1].strip()
                break
    print('The current version is {}, type a new one'.format(MESSAGE_YELLOW.format(current)))
    return current


def get_new_version():
    print(MESSAGE_GREEN.format('new version:'))
    for line in sys.stdin:
        return line.rstrip()


VERSION_FORMAT = '__version__ = "{}"\n'


def validate_release_env():
    if os.system('which twine') != 0:
        exit("Please get twine via 'pip install twine'")
    if os.system('which gitchangelog') != 0:
        exit("Please get twine via 'pip install gitchangelog' or 'pip install git+git://github.com/vaab/gitchangelog.git' for Python 3.7")


def update_version_file(version):
    new_version = VERSION_FORMAT.format(version)
    lines = []
    with open(VERSION_FILE_PATH, 'rt') as f:
        for line in f:
            if line.startswith('__version__ '):
                lines.append(new_version)
            else:
                lines.append(line)
    with open(VERSION_FILE_PATH, 'wt') as f:
        f.write("".join(lines))


def ensure_publication(new_version_num):
    if os.environ.get('DRY_RUN') is not None:
        print('Run with {} mode.'.format(MESSAGE_RED.format('[DRY_RUN]')))

    print('Are you sure to release as {}?[y/n]'.format(MESSAGE_YELLOW.format(new_version_num)))
    for line in sys.stdin:
        if line.rstrip().lower() == 'y':
            return
        exit('Canceled release.')


def call_bash_script(cmd):
    if os.environ.get('DRY_RUN') is not None:
        print('{} Calls: {}'.format(MESSAGE_RED.format('[DRY_RUN]'), cmd))
    else:
        os.system(cmd)


def commit_version_code(new_version_num):
    call_bash_script('git commit {} -m "Bump version {}"'.format(VERSION_FILE_PATH, new_version_num))


def tag_and_generate_changelog(new_version_num):
    call_bash_script('git tag "{}"'.format(new_version_num))
    call_bash_script('gitchangelog > {}'.format(CHANGELOG_PATH))
    call_bash_script('git commit {} -m "Update changelog for {}"'.format(CHANGELOG_PATH, new_version_num))


def build_sdist():
    call_bash_script('{} setup.py sdist bdist_wheel'.format(sys.executable))


def upload_sdist(new_version_num):
    call_bash_script('twine upload "dist/my_django_tweaks-{}*"'.format(new_version_num))


def push_changes_to_master(new_version_num):
    call_bash_script('git push origin master')
    call_bash_script('git push origin "{}"'.format(new_version_num))


def update_requires_io():
    call_bash_script('requires.io update - site - t ee4a1d47749c0b7f6beed8fc8e1bd2622abcf617 - r my_django_tweaks')


def main():
    validate_release_env()

    get_current_version()
    new_version = get_new_version()
    update_version_file(new_version)

    ensure_publication(new_version)

    commit_version_code(new_version)
    tag_and_generate_changelog(new_version)

    build_sdist()
    upload_sdist(new_version)

    push_changes_to_master(new_version)

    update_requires_io()


if __name__ == '__main__':
    main()
