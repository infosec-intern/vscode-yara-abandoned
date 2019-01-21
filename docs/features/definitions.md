![][logo]

# Definition Provider
Provides peeking and go-to support for the symbols in a workspace.

## Variable Definitions
Variable definitions are parsed from the `strings` section of the rule. Examples are:
* `$string = "text string"`
* `$hex_string = { DE AD BE EF }`
* `$regex = /md5: [0-9a-fA-F]{32}/`

Consult the [YARA documentation](https://yara.readthedocs.io/en/latest/writingrules.html#strings) for more information on creating variables.

![Variable definitions][def]

## Rule Definitions
Rule definitions are parsed from any lines in the file starting with `rule`.

![Rule definitions][defrule]

[logo]: https://raw.githubusercontent.com/infosec-intern/vscode-yara/master/images/logo.png "Source Image from blacktop/docker-yara"
[def]: https://raw.githubusercontent.com/infosec-intern/vscode-yara/master/images/definitions.gif "Variable definitions"
[defrule]: https://raw.githubusercontent.com/infosec-intern/vscode-yara/master/images/definition_rules.gif "Rule definitions"
