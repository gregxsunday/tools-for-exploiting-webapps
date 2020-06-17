#!/bin/sh
INFILE=$1
OUTDIR=`dirname $INFILE`
OUTFILE=$OUTDIR/domains_wo_wildcards.txt
cp $INFILE $OUTFILE
cat $OUTFILE | awk -F. '{if (NF >= 2) print $(NF-1)"."$NF;}' | sort -u | xargs -I {} sh -c "printf {}' ' ; dig +noidnout +noidnin +short *.{} | wc -l" | grep -Ev "0$" | awk '{print $1}' > $OUTDIR/wildcard_domains.txt
cat $OUTDIR/wildcard_domains.txt | xargs -I {} sed -i '/^.*\.{}/d' $OUTFILE
cat $OUTFILE | awk -F. '{if (NF >= 3) print $(NF-2)"."$(NF-1)"."$NF;}' | sort -u | xargs -I {} sh -c "printf {}' ' ; dig +noidnout +noidnin +short *.{} | wc -l" | grep -Ev "0$" | awk '{print $1}' > $OUTDIR/wildcard_domains.txt
cat $OUTDIR/wildcard_domains.txt | xargs -I {} sed -i '/^.*\.{}/d' $OUTFILE
cat $OUTFILE | awk -F. '{if (NF >= 4) print $(NF-3)"."$(NF-2)"."$(NF-1)"."$NF;}' | sort -u | xargs -I {} sh -c "printf {}' ' ; dig +noidnout +noidnin +short *.{} | wc -l" | grep -Ev "0$" | awk '{print $1}' > $OUTDIR/wildcard_domains.txt
cat $OUTDIR/wildcard_domains.txt | xargs -I {} sed -i '/^.*\.{}/d' $OUTFILE