TISSUE=${args[tissue]}

module load anaconda3
python /mnt/beegfs/merfish/sopa/cli/scripts/status.py -t $TISSUE