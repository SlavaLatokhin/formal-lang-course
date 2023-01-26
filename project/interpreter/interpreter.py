from pathlib import Path

import sys


def interpreter(*args):
    if len(args[0]) == 0:
        sys.stdout.write("No filename provided, console mode ON\n===========\n")
        program = "".join(sys.stdin.readlines())
    else:
        program = read_file(Path(args[0][0]))

    return __interpreter(program)


def read_file(filename: Path) -> str:
    try:
        script = filename.open()
    except FileNotFoundError as e:
        raise ScriptPathException(filename.name) from e

    if not filename.name.endswith(".gql"):
        raise ScriptExtensionException()

    return "".join(script.readlines())
