#!/bin/sh
set -eu

# Switch to an application's existing workspace when it requests activation
# instead of moving that application window to the current workspace.
xfconf-query -c xfwm4 -p /general/activate_action -s switch
