#!/bin/bash
OF=$1/$2.txt
rm -f $OF
touch $OF
find $1 -name "$2*.txt" -not -name $2.txt | while read line
do
    echo $line
    cat $line >> $OF
    rm $line
done
