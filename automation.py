import time
from datetime import datetime
from subprocess import *
from github import Github
import os, time, json

home = os.path.expanduser("~")

with open(f"{home}/.github") as f:
    oauth = f.read()

g = Github(oauth[6:].rstrip())

base_repo = g.get_repo("knausj85/knausj_talon")


class ForkInfo:
    def __init__(self, repo_id, repo_name, user_id, clone_url, default_branch):
        self.repo_id = repo_id
        self.repo_name = repo_name
        self.user_id = user_id
        self.clone_url = clone_url
        self.default_branch = default_branch


def base_commands():
    """Gets commands for base repo"""

    run(["git", "clone", base_repo.clone_url], encoding='utf8', cwd=f"{home}/.talon/user")
    time.sleep(1)

    run([f"{home}/.talon/bin/repl"], encoding='utf8', input=f"actions.user.base_commands()")

    run(["rm", "-rf", base_repo.name], encoding='utf8', cwd=f"{home}/.talon/user")

def get_forks():
    """Creates a file with info on all forks"""

    print("Downloading fork info...")
    forks = [ForkInfo(repo_id=fork.id, repo_name=fork.name, user_id=fork.owner.id, clone_url=fork.clone_url,
                      default_branch=fork.default_branch).__dict__
             for fork in base_repo.get_forks()]

    file_path = os.path.join(home, '.talon/user/forks.json')
    print("Creating fork info file")
    with open(file_path, "w") as write_file:
        json.dump(forks[1:], write_file, indent=4)

def alt_commands():
    """Gets commands for other repos"""

    run([f"{home}/.talon/bin/repl"], encoding='utf8', input=f"actions.user.alt_commands()")


if __name__ == '__main__':
    # base_commands()
    # get_forks()
    alt_commands()
