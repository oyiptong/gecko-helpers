#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
import shutil

CLOBBER_COMMAND = ['./mach', 'clobber']
BUILD_COMMAND = ['./mach', 'build']
GIT_CURRENT_BRANCH = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
MOZCONFIG_DEBUG_OPTS = ['--disable-optimize', '--enable-debug']
PROFILE_CHOICE_ARG = '-profile'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Firefox in a sane way')
    parser.add_argument('-g', '--git-branch', dest='git_branch', action='store_true', default=False, help='Use git branch name')
    parser.add_argument('-o', '--optimized', dest='opt', action='store_true', default=False, help='Build an optimized build')
    parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true', default=False, help='Show the resulting command')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Verbose mode')
    parser.add_argument('-p', '--profile', dest='profile_path', action='store', type=str, help='Profile path to use')
    parser.add_argument('-c', '--clobber', dest='clobber_profile', action='store_true', default=False, help='Clobber Profile')
    parser.add_argument('-P', '--purge-caches', dest='purge_caches', action='store_true', default=False, help='Purge caches')

    args = parser.parse_args()

    obj_dir_args = ['obj']
    git_branch_name = ''

    if args.git_branch:
        git_branch_name = subprocess.check_output(GIT_CURRENT_BRANCH)
        if git_branch_name:
            obj_dir_args.append(git_branch_name.lower().strip())

    nightly_package = None
    if args.opt:
        obj_dir_args.append('optimize')
        nightly_package = "Nightly.app"
    else:
        obj_dir_args.append('debug')
        nightly_package = "NightlyDebug.app"

    objdir = '_'.join(obj_dir_args)
    executable_path = '{}/dist/{}/Contents/MacOS/firefox'.format(objdir, nightly_package)

    # build command to run Firefox
    run_cmd = [executable_path, '-jsconsole']

    delete_profile = False
    if args.profile_path:
        if args.clobber_profile and os.path.isdir(args.profile_path) :
            delete_profile = True
        run_cmd.extend([PROFILE_CHOICE_ARG, args.profile_path])

    if args.purge_caches:
        run_cmd.append('-purgecaches')

    if args.dry_run or args.verbose:
        print """
> DRY-RUN Mode

clobber_profile: {}

run command:

{}""".format(delete_profile, ' '.join(run_cmd))
        if args.dry_run:
            sys.exit(0)

    if delete_profile:
        shutil.rmtree(args.profile_path)

    os.execv(run_cmd[0], run_cmd)
