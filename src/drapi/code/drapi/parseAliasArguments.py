"""
Parse variable alias arguments in package scripts.
"""

from typing_extensions import Dict

# Custom argument parsing: aliases


def parseAliasArguments(customAliases: Dict[str, str],
                        useDefaultAliases: bool,
                        defaultAliases: Dict[str, str]) -> Dict[str, str]:
    """
    Parse variable alias arguments in package scripts.
    """
    if customAliases:
        customAliases = dict(customAliases)  # For type hinting
    if customAliases and useDefaultAliases:
        variableAliases = defaultAliases.copy()
        listOfAliasesToOverwrite = sorted(list(set(customAliases.keys()).intersection(set(variableAliases.keys()))))
        if len(listOfAliasesToOverwrite) > 0:
            print(f"""WARNING: The following aliases are being over-written by your custom input:\n{listOfAliasesToOverwrite}.""")
        variableAliases.update(customAliases)
    elif customAliases:
        variableAliases = customAliases.copy()
    elif useDefaultAliases:
        variableAliases = defaultAliases.copy()
    else:
        variableAliases = {}
    return variableAliases
