#!/usr/bin/env python
import os
import sys
import argparse
import subprocess

CLOBBER_COMMAND = ['./mach', 'clobber']
BUILD_COMMAND = ['./mach', 'build']
GIT_CURRENT_BRANCH = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
MOZCONFIG_DEBUG_OPTS = ['--disable-optimize', '--enable-debug']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Firefox in a sane way')
    parser.add_argument('-c', '--clobber', dest='clobber', action='store_true', default=False, help='Build from scratch')
    parser.add_argument('-g', '--git-branch', dest='git_branch', action='store_true', default=False, help='Build incrementally')
    parser.add_argument('-o', '--optimized', dest='opt', action='store_true', default=False, help='Build an optimized build')
    parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true', default=False, help='Show the resulting command')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Verbose mode')
    parser.add_argument('infiles', metavar='FILENAME', nargs='*')

    args = parser.parse_args()

    mozconfig_options = []

    # generate mozconfig
    obj_dir_args = ['obj']
    git_branch_name = ''

    if args.git_branch:
        git_branch_name = subprocess.check_output(GIT_CURRENT_BRANCH)
        if git_branch_name:
            obj_dir_args.append(git_branch_name.lower().strip())

    if args.opt:
        obj_dir_args.append('optimize')
    else:
        obj_dir_args.append('debug')
        mozconfig_options.extend(MOZCONFIG_DEBUG_OPTS)

    mozconfig_objdir = '_'.join(obj_dir_args)

    mozconfig_filename = './.mozconfig_{}'.format('_'.join(obj_dir_args[1:]))
    mozconfig_file_content = 'mk_add_options MOZ_OBJDIR={}'.format(mozconfig_objdir)
    for opt in mozconfig_options:
        mozconfig_file_content += '\nac_add_options {}'.format(opt)

    # generate build command
    build_cmd = None

    if args.clobber:
        build_cmd = CLOBBER_COMMAND
    else:
        build_cmd = BUILD_COMMAND

    build_cmd.extend(args.infiles)

    if args.dry_run or args.verbose:
        print """
> DRY-RUN Mode

mozconfig filename:

{0}

mozconfig file contents:

{1}

environment:

MOZCONFIG={0}

mach command:

{2}""".format(mozconfig_filename, mozconfig_file_content, ' '.join(build_cmd))
        if args.dry_run:
            sys.exit(0)

    with open(mozconfig_filename, 'w') as f:
        f.write(mozconfig_file_content)

    os.putenv('MOZCONFIG', mozconfig_filename)
    os.execv(build_cmd[0], build_cmd)
