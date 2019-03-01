from distutils.core import setup
import os

setup(
    name="yarals",
    description="YARA Language Server for Visual Studio Code",
    author="Infosec Intern",
    author_email="thomas@infosec-intern.com",
    download_url="https://github.com/infosec-intern/vscode-yara",
    url="https://infosec-intern.github.io/vscode-yara/",
    version="0.1",
    packages=["yarals"],
    package_data={"yarals": ["data/*.json"]},
    provides=["yarals"],
    requires=["yara-python"],
    scripts=["vscode_yara.py"]
)
