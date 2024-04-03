# *sopa* usage on Flamingo

A Command Line Interface (CLI) is used to call and monitor the pipelines on Flamingo. It uses [Bashly](https://bashly.dannyb.co/), a CLI framework.

## Getting started

1. Add `source /mnt/beegfs/merfish/sopa/igr-cli/.sopa_bashrc` to your `~/.bashrc` file
2. Edit (or create) your `~/.condarc` file to add the envs located inside sopa:
```sh
envs_dirs:
  - /mnt/beegfs/userdata/q_blampey/.conda/envs
  - /mnt/beegfs/merfish/.conda/envs
```

Now, open a new Flamingo session to use these changes, and simply run the CLI as follow (this is a helper that shows all the available commands):

```sh
sopa-igr -h
```

### Optional SSH setup

We recommend to create **locally** a new ssh host called `flamingo` to ease the access to it from your terminal. This enables access to flamingo by simply running `ssh flamingo`.

1. **Locally**, create a new RSA key called `~/.ssh/id_rsa_flamingo` using the following command: `ssh-keygen -t rsa`
2. Add and update the lines below to your `~/.ssh/config` file:
```sh
Host flamingo
   HostName flamingo.intra.igr.fr
   User q_blampey   # update it with your flamingo username
   IdentityFile ~/.ssh/id_rsa_flamingo
```
1. Run `ssh-copy-id -i ~/.ssh/id_rsa_flamingo flamingo` to add your RSA key on flamingo

## Usage

To run the pipeline, simply execute `sopa-igr run` (outside of a conda env), and answer to the prompts. Once the pipeline is starting, you can close the window, or press "ctrl+a+d" to exit (the pipeline will continue running).

> Troobleshooting: if you get an error about `PyICU`, you can run the following command (once): `module load anaconda3 && pip install --user PyICU`

All processed files can then be found inside `/mnt/glustergv0/MERFISH/data`

## File system and data storage on **Flamingo**

This git repository only contains code for the pipeline, i.e. it doesn't work on its own. Indeed, it is included inside many other directories on Flamingo, which contains data, logs, or also all the `conda` environments needed to run the pipeline.

### Merfish directory

```
# /mnt/beegfs/merfish    <- accessible via 'cd $MERFISH'
.
├── .conda
│   ├── envs         # contains all the conda envs needed
│   └── yml_backups  # yaml files to create the conda envs
├── data
│   ├── <TISSUE>
│   │   └── <SLIDE>
│   │       └── <REGION> # one sample (i.e. one patient) directory
│   └── reference        # annotated scRNAseq references for Tangram
├── sopa        # this git repository
├── bin         # binary executables, e.g. baysor
├── results     # unstructured output files (sandbox)
└── scripts     # .sh scripts (not from the pipeline)
```

### Cold storage
The above directory is not meant for long term storage, but only for computation. Thus, in order to store all the raw data and the processed outputs of the pipeline, we also made a cold storage directory.

When acquired, files from the MERSCOPE are first sent to the cold storage. Then, when running the pipeline, files are copied to the above Merfish directory. Afterwards, when the files have been processed by the pipeline, they are saved back on the cold storage (and can be deleted from the hot storage).

```
# /mnt/glustergv0/MERFISH    <- accessible via 'cd $GLUSTER_MERFISH'
.
├── raw    # MERSCOPE intermediate files (not used by the pipeline)
├── data     # MERSCOPE outputs
│   └── <TISSUE>
│       └── <SLIDE>
│           └── <REGION> # one sample (i.e. one patient) directory
└── processed  # pipeline outputs
    └── <TISSUE>
        └── <SLIDE>
            └── <REGION>.explorer # outputs of one pipeline run
```

Since post-analysis is based only on the pipeline outputs, we can synchronize the pipeline ouputs from the cold storage into a local directory:
```sh
rsync -var flamingo:/mnt/glustergv0/MERFISH/processed <path_to_local_directory>
```

For simplicity, you can also use an application such as CyberDuck to transfer your files locally (drag and drop).

# Contributing

## Add new sopa functionnalities

To contribute to the main `sopa` repository, refer to our [CONTRIBUTING.md](https://github.com/gustaveroussy/sopa/blob/master/CONTRIBUTING.md) file.

To implement new functionalities specific to Gustave Roussy, use the branch `igr`.

## Updating the `igr-cli`

First, install Bashly as written in [their installation guidelines](https://bashly.dannyb.co/installation/).

Then, use the `igr` branch, go to the root of the project, and move to the `igr-cli` subdirectory.

The different subcommands and their arguments can be found inside `src/bashly.yml`. You can refer to [the Bashly documentation](https://bashly.dannyb.co/) to add a new command.

For each command, there is an associated `.sh` file that will be run, with the arguments listed in the `bashly.yml` file. For instance, the `status` command will execute the `src/status_command.sh` file, and the arguments are accessible inside the shell file using `args`, e.g. `TISSUE=${args[tissue]}`.

> NB: some python scripts were added in the `scripts` directory, but this is not related to Bashly.

Once you made some changes, you can generate a new CLI shell file (i.e., the `sopa-igr` file) by running:

```sh
bashly generate
```

Then, don't forget to push your changes on Github, and run `sopa-igr update` to pull the changes on flamingo.
