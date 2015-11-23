#!/usr/bin/env python
import argparse
import sys
import re

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a branch name from a bug description")
    parser.add_argument('bug_names', metavar='BUG_NAME', nargs='+')

    args = parser.parse_args()

    for bug_name in args.bug_names:
        branch_name = '_'.join(re.sub(r'__+', '_', re.sub(r'[\W\s]', '_', bug_name.strip().lower())).split('_'))
        print branch_name
