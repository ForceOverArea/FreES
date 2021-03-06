from requests import get
from os import listdir, path


def fchk():
    """Returns a dict of outdated files and the latest version of their code."""
    change = {}

    for file in listdir():

        if file == "__pycache__":
            continue
        
        with open(file, 'r') as f:
            current = f.read()
            latest = get(f"https://github.com/ForceOverArea/FreES/raw/main/program/{file}").text

        if current != latest:
            change[file] = latest

    return change


def sync():
    """Syncs the libraries with the current repo version."""

    updates = fchk()

    confirm = input(f"The following files will be synced with Github: {updates.keys()}\n\nDo you still wish to proceed? ['NO'/'yes']")

   

    if confirm == "yes":
        print("Syncing files...")
        for file in updates:
            with open(file, 'w') as f:
                f.write(updates[file])
        print("Done.")

    else:
        print("Cancelled operation.")
            
sync()
