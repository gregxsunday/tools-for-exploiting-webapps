#!/bin/bash
python3 get-good-resolvers.py
parallel -j 100 "./list-bad-resolvers.sh {}" :::: good-resolvers.txt > bad-resolvers.txt
cat bad-resolvers.txt | xargs -I{} sed -i "/{}/d" good-resolvers.txt
