FILE="${args[file]:-1}"

if [ ${#FILE} -eq 7 ]; then
    cat /mnt/beegfs/merfish/sopa/workflow/logs/$FILE
    echo
    echo "[Job log file $FILE]"
    echo
else
    re='^[0-9]+$'

    if [[ $FILE =~ $re ]] ; then
        FILE="$(ls -rt /mnt/beegfs/merfish/sopa/workflow/.snakemake/log | tail -n${FILE} | head -1)"
    fi

    FULL_PATH=/mnt/beegfs/merfish/sopa/workflow/.snakemake/log/$FILE
    OWNER="$(stat -c '%U' $FULL_PATH)"

    cat $FULL_PATH
    echo
    echo "[Snakemake log file $FILE - executed by $OWNER]"
fi
