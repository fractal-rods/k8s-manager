import re as re
from sys import argv

pattern = re.compile(
    "^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    "{1}(\([\w\-\.]+\))?(!)?: ([\w ])+([\s\S]*)"
)

if len(argv) != 2:
    print("Wrong number of arguments!")
    exit(1)

if re.search(pattern, argv[1]) is not None:
    print("Title matched!")
    exit(0)
else:
    print("Title does not match!")
    exit(1)
