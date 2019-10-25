import subprocess
import os
import sys

from subprocess import PIPE

STEPS = "Step:"
RESULT = "Result:"
SETUP = "Setup:"

def enter_depend_test():

    # Simple magic for using scripts within a source tree
    BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(BASEDIR, 'depend_test_framework')):
        os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'examples')
        sys.path.insert(0, BASEDIR)

def run_cmd(cmd):
    return subprocess.check_output(cmd.split())

def run_shell(cmd):
    return subprocess.run(cmd, check=False, shell=True, stdout=PIPE, stderr=PIPE)
