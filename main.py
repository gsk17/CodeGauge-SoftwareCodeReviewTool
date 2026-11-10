"""CO7095 Software Code Review Tool - entry point.

Launches the text menu. There is no GUI and no database by design: the
assignment brief asks for backend functionality only, with persistence in a
serialised text file.
"""


def main() -> None:
    """Print the banner and hand control to the menu loop."""
    print("CO7095 CODE REVIEW TOOL")
    # The menu loop is wired in here by the CLI user story (plan Task 9).


if __name__ == "__main__":
    main()
