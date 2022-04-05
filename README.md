# Talon Command Extractor
Extracts command mappings from Talon into a JSON file. To use it, follow these steps:
1. Copy `extract.py` into `~/.talon/user`
2. You will need to run `automation.py` in a different virtual environment where you have PyGithub installed. PyGithub does not work when you install it using the pip provided in Talon. I am running `automation.py` from PyCharm.
3. The script assumes you don't have anything in `~/.talon/user` aside from `extract.py`
4. It will first clone the base repo and create a file of base commands.
5. Then it will query Github for a list of forks and create a json file with info about the forks.
6. Then it will go through the forks and clone them one by one and create a file with all the alternative commands as well as a file listing the forks that had errors.
7. The errors are mostly related to Talon taking a while to process a new set of commands. There is a constant near the top of `extract.py` called `SLEEP_TIME` which represents the number of seconds (can be floating point) it will sleep after cloning a new repo. Most of them will work with as little as 1 second but some take longer. It may be worth running it once with a lower number and reprocessing the errors with a higher number.
8. I've changed it so that the errors file has a structure similar to the fork info file. This way if you want, you can rename the errors file to `forks.json` and rerun the last part of the script.
9. If you already have a base commands file and a forks file and you just want to run the last part of the script, you can comment out `base_commands()` and `get_forks()` near the end of `automation.py`
