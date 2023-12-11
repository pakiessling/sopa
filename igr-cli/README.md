# *sopa-igr* CLI

This Command Line Interface (CLI) is intended to call and monitor the pipelines on flamingo.

It uses [Bashly](https://bashly.dannyb.co/), a CLI framework.

## Getting started

The pipeline can be run by executing the `sopa-igr` file, i.e.

```sh
./sopa-igr
```
**On flamingo**, there is an alias inside `/mnt/beegfs/merfish/sopa/igr-cli/.sopa_bashrc` so that the CLI is called by running only `sopa-igr`. For instance, you can run the following line to get a helper:

```sh
sopa-igr -h
```

## Updating the pipeline

First, install Bashly as written in [their installation guidelines](https://bashly.dannyb.co/installation/).

The different subcommands and their arguments can be found inside `src/bashly.yml`. You can refer to [the Bashly documentation](https://bashly.dannyb.co/) to add a new command.

For each command, there is an associated `.sh` file that will be run, with the arguments listed in the `bashly.yml` file. For instance, the `status` command will execute the `src/status_command.sh` file, and the arguments are accessible inside the shell file using `args`, e.g. `TISSUE=${args[tissue]}`.

> NB: some python scripts were added in the `scripts` directory, but this is not related to Bashly.

Once you made some changes, you can generate a new CLI shell file (i.e., the `sopa-igr` file) by running:

```sh
bashly generate
```

Then, don't forget to push your changes on Github, and run `sopa-igr update` to pull the changes on flamingo.