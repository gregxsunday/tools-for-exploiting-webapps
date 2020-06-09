#!/bin/bash

RESOLVER=$1

RES=`dig +short @$RESOLVER no.existing.domain.asd`
if [[ ${#RES} -ne 0 ]] 
then
	echo $RESOLVER
fi
