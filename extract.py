import time

from talon import Module, actions, registry
from datetime import datetime
from subprocess import *
import sys, os, json


SLEEP_TIME = 30


class CommandGroup:
    def __init__(self, file, context, commands):
        self.file = file
        self.context = context
        self.commands = commands


class UserCommands:
    def __init__(self, repo_id, user_id, timestamp, branch, command_groups):
        self.repo_id = repo_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.branch = branch
        self.command_groups = command_groups


def key_commands(list_name):
    command_list = registry.lists[list_name][0]
    return CommandGroup('code/keys.py', list_name, command_list)


def formatters():
    command_list = registry.lists['user.formatters'][0]
    command_list = {key: actions.user.formatted_text(f"example of formatting with {key}", key) for key in command_list}
    return CommandGroup("code/formatters.py", "user.formatters", command_list)


def context_commands(commands):
    # write out each command and its implementation
    rules = {}
    for key in commands:
        try:
            rule = commands[key].rule.rule
            implementation = commands[key].target.code  # .replace("\n", "\n\t\t")
        except Exception:
            continue
        lines = [line for line in implementation.split("\n") if line and line[0] != "#"]
        rules[rule] = "\n".join(lines)

    return rules


def format_context_name(name):
    # The logic here is intended to only get contexts from talon files that have actual voice commands.
    splits = name.split(".")
    index = -1

    os = ""

    if "mac" in splits:
        os = "mac "
    if "win" in splits:
        os = "win "
    if "linux" in splits:
        os = "linux "

    if "talon" in splits[index]:
        index = -2
        short_name = splits[index].replace("_", " ")
    else:
        short_name = splits[index].replace("_", " ")

    if "mac" == short_name or "win" == short_name or "linux" == short_name:
        index = index - 1
        short_name = splits[index].replace("_", " ")

    return f"{os}{short_name}"


def format_file_name(name):
    splits = name.split(".")
    base_file_name = "/".join(splits[2:-1])
    extension = splits[-1]

    return f"{base_file_name}.{extension}"


def resolve_dup(full_name1, full_name2, formatted_name):
    splits1 = full_name1.split("/")
    splits2 = full_name2.split("/")

    index = -2
    try:
        while splits1[index] == splits2[index]:
            index -= 1
        names = f"{formatted_name} ({splits1[index]})", f"{formatted_name} ({splits2[index]})"
    except IndexError:
        names = f"{formatted_name} (1)", f"{formatted_name} (2)"

    return names


def user_commands(repo_id, user_id, timestamp, branch):

    key_command_names = ['user.letter', 'user.number_key', 'user.modifier_key', 'user.special_key',
                         'user.symbol_key', 'user.arrow_key', 'user.punctuation', 'user.function_key']

    # Storing these in a dict makes it easier to detect duplicates
    command_groups = {name: key_commands(name) for name in key_command_names if name in registry.lists}

    # Add formatters
    command_groups["user.formatters"] = formatters()

    # Get all the commands in all the contexts
    list_of_contexts = registry.contexts.items()
    for name, context in list_of_contexts:
        commands = context.commands  # Get all the commands from a context
        if len(commands) > 0:
            context_name = format_context_name(name)
            file_name = format_file_name(name)

            # If this context name is a duplicate, create new names and update the dict
            if context_name in command_groups:
                other = command_groups.pop(context_name)
                other.context, context_name = resolve_dup(other.file, file_name, context_name)
                command_groups[other.context] = other

            command_groups[context_name] = CommandGroup(file_name, context_name, context_commands(commands))

    command_groups = [command_group.__dict__ for command_group in command_groups.values()]

    return UserCommands(repo_id=repo_id, user_id=user_id, timestamp=timestamp, branch=branch, command_groups=command_groups)


mod = Module()


@mod.action_class
class Actions:
    def base_commands():
        """Creates a JSON file of talon commands"""

        this_dir = os.path.dirname(os.path.realpath(__file__))
        repo_dir = os.path.join(this_dir, "knausj_talon")

        commands = user_commands(repo_id="240185541", user_id="15005956", timestamp=datetime.now().isoformat(), branch="master")
        file_path = os.path.join(this_dir, 'base_commands.json')
        print("Creating base commands file")
        with open(file_path, "w") as write_file:
            json.dump(commands.__dict__, write_file, indent=4)

    def alt_commands():
        """Creates a file of alternative voice commands"""

        this_dir = os.path.dirname(os.path.realpath(__file__))

        file_path = os.path.join(this_dir, 'forks.json')
        with open(file_path, "r") as read_file:
            forks = json.load(read_file)

        file_path = os.path.join(this_dir, 'base_commands.json')
        with open(file_path, "r") as read_file:
            base_commands = json.load(read_file)

        base_commands = {command_group["context"]: CommandGroup(file=command_group["file"], context=command_group["context"], commands=command_group["commands"])
                         for command_group in base_commands["command_groups"]}

        errors = []
        alt_commands = []
        for fork in forks:
            repo_dir = os.path.join(this_dir, fork["repo_name"])
            print(f"Getting commands for user {fork['user_id']}")
            run(["git", "clone", fork["clone_url"]], encoding='utf8', cwd=this_dir)
            print(f"Sleeping for {SLEEP_TIME}s")
            time.sleep(SLEEP_TIME)
            try:
                alt_commands.append(user_commands(repo_id=fork["repo_id"], user_id=fork["user_id"], timestamp=datetime.now().isoformat(), branch=fork["default_branch"]))
            except RuntimeError:
                errors.append(fork)
                continue
            run(["rm", "-rf", repo_dir], encoding='utf8')

        for user_data in alt_commands:
            for command_group in user_data.command_groups:
                context = command_group["context"]
                command_group["commands"] = {invocation: target for invocation, target in command_group["commands"].items()
                                          if context in base_commands
                                          and invocation not in base_commands[context].commands
                                          and target in base_commands[context].commands.values()}

            user_data.command_groups = [cg for cg in user_data.command_groups if cg["commands"]]

        file_path = os.path.join(this_dir, 'alt_commands.json')
        with open(file_path, "w") as write_file:
            json.dump([user_data.__dict__ for user_data in alt_commands], write_file, indent=4)

        file_path = os.path.join(this_dir, 'errors.json')
        with open(file_path, "w") as write_file:
            json.dump(errors, write_file, indent=4)

