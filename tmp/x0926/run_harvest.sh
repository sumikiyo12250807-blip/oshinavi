cd /c/Users/user/oshinavi
export PYTHONIOENCODING=utf-8
for lg in 01 02 03 04 05 06 07; do for st in 0102 0202; do
  python tools/presale_harvest.py $lg tmp/x0926/presale_${lg}_${st}.json rlsStatus=$st > tmp/x0926/presale_${lg}_${st}.log 2>&1
  echo "$lg $st rc=$?" >> tmp/x0926/harvest_done.txt
done; done
echo ALLDONE >> tmp/x0926/harvest_done.txt
