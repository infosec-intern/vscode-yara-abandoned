from setuptools import setup

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
    install_requires=["yara-python"],
    tests_require=["pytest", "pytest-asyncio"],
    scripts=["vscode_yara.py"]
)
