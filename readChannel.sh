#/bin/bash
set -x
minofhour=`date +%M`
step=5
remainder=$(( ${minofhour}%${step} ))
if [ ${remainder} == 0 ] || [ ${minofhour} == 0 ]
then
	/home/gerard/readChannel.py > /home/gerard/readChannel.py.out 2>&1
fi
exit 0
