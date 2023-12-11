TISSUE=${args[tissue]}

module load anaconda3
python /mnt/beegfs/merfish/sopa/igr-cli/scripts/status.py -t $TISSUE