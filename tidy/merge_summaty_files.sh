
# directories to compare
COMP1='/Users/michael/comptest/comp1'
COMP2='/Users/michael/comptest/comp2'
# merge directory
MERGE='/Users/michael/comptest/merge'
#
# create merge directiry if it does not exist
mkdir -p $MERGE
# create list of files whch are only in one of the two directories
# list=($(diff -r ~/comptest/comp1 ~/comptest/comp2 --brief  | sed 's/^Only in \([^:]*\): /\1\//' | sed 's/^Files \(.*\) and .* differ/\1/'))
LIST=($(diff -r $COMP1 $COMP2 --brief  | sed 's/^Only in \([^:]*\): /\1\//' | sed 's/^Files \(.*\) and .* differ/\1/'))

# write out the list
echo $list
# copy those files to the merge directory

#

/Users/michael/comptest/comp1/M02813_summary.csv
mimas:summaries michael$ 