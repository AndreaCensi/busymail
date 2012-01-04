#!/bin/bash
set -e
source /Users/andrea/scm/usrpyplus.sh
root=/Users/andrea/scm-pri/busymail/

export PATH=/usr/local/bin:$PATH

out=$root/output
mkdir -p $out
python $root/busyplot.py $root/busylog/ $out

when=`python $root/when.py`

convert  -family serif -pointsize 14 -fill blue "label:$when" $out/updated.gif 2>/dev/null

# rsync --quiet -av $out/ andrea@escondido:scm/andreaweb/src/busyplot 2>/dev/null
# rsync --quiet -av $out/ andrea@escondido:scm/andreaweb/output/busyplot 2>/dev/null


rsync --quiet -av $out/ andrea@kincora.cds.caltech.edu:public_html/busyplot 2>/dev/null
