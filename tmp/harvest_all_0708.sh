set -e
declare -a JOBS=("01:rlsIn=04:music04" "02:rlsIn=03:engeki03" "07:rlsIn=03:classic03" "05:rlsIn=03:art03" "06:rlsIn=03:event03")
for j in "${JOBS[@]}"; do
  lg="${j%%:*}"; rest="${j#*:}"; flt="${rest%%:*}"; tag="${rest##*:}"
  out="tmp/presale_${tag}_0708.json"
  python tools/presale_harvest.py "$lg" "$out" "$flt" > "tmp/hv_${tag}.log" 2>&1 || echo "FAIL $tag"
  n=$(python -c "import json;print(len(json.load(open('$out',encoding='utf-8'))))" 2>/dev/null || echo ERR)
  echo "$tag : $n 件"
  sleep 8
done
echo "ALL DONE"
