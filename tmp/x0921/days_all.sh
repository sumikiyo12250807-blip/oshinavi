cd /c/Users/user/oshinavi
for lg in 01 02 07 06 03 04 05; do python -u tmp/x0921/pia_days_list.py $lg > tmp/x0921/pia_days_$lg.txt 2>&1; done
echo DONE
