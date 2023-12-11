LOG_FILE=${args[file]}

module load anaconda3
python /mnt/beegfs/merfish/sopa/igr-cli/scripts/parse_logs.py -p /mnt/beegfs/merfish/sopa/workflow/.snakemake/log/$LOG_FILE