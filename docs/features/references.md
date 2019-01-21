![][logo]

# Symbol References
Finds all references for a symbol selected in a YARA rule.

## Variables
If the symbol is a variable, only the local rule is searched.

![][ref]

## Rules
If the symbol is a rule name, the entire file is searched.

![][refrule]

## Wildcards
Variable wildcards are a special case; attempting to resolve their references shows the reference for all variables that that wildcard covers.

![][refwild]

[logo]: ../../images/logo.png "Source Image from blacktop/docker-yara"
[ref]: ../../images/references_normal.gif "All Variable Reference"
[refrule]: ../../images/references_rules.gif "All Rule Reference"
[refwild]: ../../images/references_wildcard.gif "All Wildcard References"