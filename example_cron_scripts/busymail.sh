#!/bin/bash
set -e
# set -x
source /Users/andrea/scm/usrpyplus.sh
root=/Users/andrea/scm-pri/busymail/
python $root/busymail.py $root/busylog/

git="/usr/local/git/bin/git  --git-dir=$root/.git --work-tree=$root"
$git add  $root/busylog/*.yaml >/dev/null 
$git commit -m "update `python $root/when.py`" >/dev/null
$git push  >/dev/null  2>/dev/null