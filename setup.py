import os

from setuptools import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('sapien_viz/assets')

setup(
    install_requires=open("requirements.txt").read(),
    package_data={'sapien_viz': extra_files},
)
