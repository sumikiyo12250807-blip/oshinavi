set -e
for lg in 01 02 03 04 05 06 07; do
  for st in 0102 0202; do
    python tools/pia_sweep_all.py $lg tmp/_sw_${lg}_${st}_0902.json rlsStatus=$st >> tmp/_sweep_0902.log 2>&1
  done
done
echo "SWEEP_DONE"
