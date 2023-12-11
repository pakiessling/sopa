screen sh -c "\
    module load anaconda3 &&\
    source activate snakemake &&\
    cd /mnt/beegfs/merfish/sopa/workflow &&\
    python /mnt/beegfs/merfish/sopa/igr-cli/scripts/prompt.py &&\
    echo 'Exiting screen in 60s...(or run ctrl+C to exit now)' &&\
    sleep 60"