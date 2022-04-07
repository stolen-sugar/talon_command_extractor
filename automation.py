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
    def __init__(self, repo_id, repo_name, user_id, clone_url, parent, branches):
        self.repo_id = repo_id
        self.repo_name = repo_name
        self.user_id = user_id
        self.clone_url = clone_url
        self.parent = parent
        self.branches = branches


def base_commands():
    """Gets commands for base repo"""

    run(["git", "clone", base_repo.clone_url], encoding='utf8', cwd=f"{home}/.talon/user")
    time.sleep(30)

    run([f"{home}/.talon/bin/repl"], encoding='utf8', input=f"actions.user.base_commands()")

    run(["rm", "-rf", base_repo.name], encoding='utf8', cwd=f"{home}/.talon/user")

def get_forks():
    """Creates a file with info on all forks"""

    # base_branches = {branch.name for branch in base_repo.get_branches()}

    personal_branches = {"experimental","test_new","zmcgohan","ryan_personal","bryan","vinu-copy","replace-words","twiebelt","nat-customizations","fork","home","customize","CameronScottBell","main","gaute-main","David_customization","customizations","user/dyancat","my-stuff","mzizzi","vivshaw-talon-scripts","bkd/mouse_commands","grant","bn","gh-trimmed","ghouston-master","pavel","ajy","ajy2","eli/tweaks","luis","ViacheslavKudinov-patch-1","ViacheslavKudinov-patch-2","vadim_personal","mine","shawnp/custom","bietola-personal","ark","jay51","custom","custom-07092021","cz","my-talon","amongus","aedison-working","1-aedison-working-branch","hellsan631/changes","create-spoken-forms","paul-jones","vocab-symbols","customization3","customization","geeogi","rd","wolle_personal","wolle","terry","rubymine","joeversion","jp","jessica","bhipple","local","lexjacobs","lexjacobs-bak","my-config","my-config2","personal2","livioso","own_vocab","trapiers","changes","jjh-branch"}

    print("Downloading fork info...")
    forks = [ForkInfo(repo_id=fork.id, repo_name=fork.name, user_id=fork.owner.id, clone_url=fork.clone_url, parent=fork.parent.id,
                      branches=[branch.name for branch in fork.get_branches()])
             for fork in base_repo.get_forks()]

    forks = {fork.repo_id: fork for fork in forks}
    for fork in forks.values():
        fork.branches = [branch for branch in fork.branches if fork.repo_id != base_repo.id and branch in personal_branches]
        if fork.parent in forks:
            fork.branches = [branch for branch in fork.branches if branch not in forks[fork.parent].branches]

    file_path = os.path.join(home, '.talon/user/branches.json')
    print("Creating fork info file")
    with open(file_path, "w") as write_file:
        json.dump([fork.__dict__ for fork in forks.values() if fork.branches][1:], write_file, indent=4)

def alt_commands():
    """Gets commands for other repos"""

    run([f"{home}/.talon/bin/repl"], encoding='utf8', input=f"actions.user.alt_commands()")


if __name__ == '__main__':
    # base_commands()
    # get_forks()
    alt_commands()
