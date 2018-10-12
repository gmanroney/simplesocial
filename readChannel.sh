#/bin/bash
. ./setenv
minofhour=`date +%M`
exec > ${homedir}/logs/readChannel.${minofhour}.py.out 2>&1
set -x
step=5
remainder=$(( ${minofhour}%${step} ))
if  [ ${remainder} -eq 0 ] || [ ${minofhour} -eq 0 ] 
then
	echo "[`date`] Starting execution"
	${homedir}/readChannel.py 
	echo "[`date`] Stopping execution"
fi
exit 0
