import os
import subprocess
import sys


cache_root = 'cache'
pyenv_root = os.path.join(cache_root, 'pyenv')


def check_call(args, *pargs, **kwargs):
    args = list(args)
    print('Launching: ')
    for arg in args:
        print('    {}'.format(arg))

    return subprocess.check_call(args, *pargs, **kwargs)


def get_url(url, path):
    check_call(
        [
            'curl',
            '-L',
            '-o', path,
            url,
        ],
    )


def python_name_from_version(version):
    version = '.'.join(version.replace('-', '.').split('.')[:2])

    if version.startswith('pypy'):
        return version

    return 'python{}'.format(version)


def install_python_linux(version):
    archive_file = 'python_archive'
    url = (
        'https://s3.amazonaws.com'
        '/travis-python-archives/binaries/ubuntu/16.04/x86_64'
        '/python-{}.tar.bz2'.format(version)
    )

    get_url(url=url, path=archive_file)

    check_call(
        [
            'sudo',
            'tar',
            'xjf',
            archive_file,
            '--directory', '/',
        ],
    )

    return python_name_from_version(version)


class PyEnv:
    def __init__(self, root):
        self.root = root

    @classmethod
    def install(cls, root):
        root_parent = os.path.dirname(root)
        os.makedirs(root_parent, exist_ok=True)

        archive = 'pyenv_archive.zip'

        get_url(
            url='https://github.com/pyenv/pyenv/archive/master.zip',
            path=archive,
        )

        check_call(['unzip', '-d', root_parent, archive])
        os.rename(
            src=os.path.join(root_parent, 'pyenv-master'),
            dst=pyenv_root,
        )

        pyenv = cls(root=root)

        pyenv.run('rehash')

        return pyenv

    def python_path(self, version):
        return os.path.join(
            self.root,
            'shims',
            python_name_from_version(version),
        )

    def run(self, *args):
        env = dict(os.environ)
        env['PYENV_ROOT'] = self.root

        command = (os.path.join(self.root, 'bin', 'pyenv'),)
        command += args

        check_call(command, env=env)


def install_python_darwin(version):
    pyenv = PyEnv.install(root=pyenv_root)
    pyenv.run('install', version)
    pyenv.run('global', version)

    return pyenv.python_path(version)


def platform_dispatch(d, *args, **kwargs):
    for name, f in d.items():
        if sys.platform.startswith(name):
            return f(*args, **kwargs)
    else:
        raise Exception('Platform not supported: {}'.format(sys.platform))


def install_python(*args, **kwargs):
    d = {
        'linux': install_python_linux,
        'darwin': install_python_darwin,
        # 'win': install_python_windows,
    }

    return platform_dispatch(d, *args, **kwargs)


def get_virtualenv(version):
    url = 'https://github.com/pypa/virtualenv/archive/{}.zip'.format(version)

    path = 'virtualenv_archive'

    get_url(url=url, path=path)

    check_call(
        [
            'unzip',
            path,
        ],
    )

    return 'virtualenv-{}'.format(version)


def main():
    version = os.environ['PYTHON']
    python_path = install_python(version)

    virtualenv_path = get_virtualenv('16.2.0')

    env_path = '.venv'

    env = dict(os.environ)
    env['PYTHONPATH'] = virtualenv_path

    check_call(
        [
            python_path,
            '-m', 'virtualenv',
            env_path,
        ],
        env=env,
    )


main()
