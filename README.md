# Abandoned

I've decided to abandon this particular version of the project. It's been several years since I started building this version and, while I've made progress on the language server, other unforeseen problems keep popping up with this implementation.

The good news is that I've learned a whole lot about Typescript in the meantime, and I should be able to port most of the features I previously thought could only be done in Python into the existing Typescript-based extension (previously located at textmate-yara, now renamed to [vscode-yara](https://github.com/infosec-intern/vscode-yara)).

I have moved the Python-based language server into its own repository ([ch0mler/yara-language-server](https://github.com/ch0mler/yara-language-server/)) and uploaded the package to PyPi ([yara-language-server](https://pypi.org/project/yara-language-server/)) in case anyone is interested in continuing that work or re-implementing it in another language or for another platform.

I apologize if this is confusing, but I hope that these changes will help make the project better for everyone.

As always, please don't hesitate to open an [Issue](https://github.com/infosec-intern/vscode-yara/issues) or a [Pull Request](https://github.com/infosec-intern/vscode-yara/pulls)!
