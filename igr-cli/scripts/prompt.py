import subprocess
from pathlib import Path
from typing import List, Optional

from dotenv import dotenv_values
from InquirerPy import inquirer


def is_valid(p: Path, dir_only: Optional[bool], suffix: Optional[str]):
    if dir_only is not None and p.is_dir() != dir_only:
        return False
    if suffix is not None and p.suffix != suffix:
        return False
    return True


def search(
    path: Path,
    is_dir: Optional[bool] = True,
    suffix: Optional[str] = None,
    return_path: bool = False,
) -> List[Path]:
    choices = [
        p if return_path else p.name
        for p in sorted(list(path.iterdir()))
        if is_valid(p, is_dir, suffix)
    ]

    if not choices:
        raise ValueError(f"No valid file/subdirectory inside {path}")
    return choices


def run(data_path: Path, config_path: str, suffix: str):
    (data_path / "images").mkdir(parents=True, exist_ok=True)

    sdata_path = data_path.parent / f"{data_path.stem}{suffix}.zarr"

    print(f"The SpatialData output will be {sdata_path}")
    print("Starting pipeline... (you can exit with ctrl+a+d)")
    try:
        subprocess.run(
            f"""snakemake --config data_path={data_path} sdata_path={sdata_path} --configfile={config_path} --profile slurm --rerun-triggers mtime params input code""",
            shell=True,
            check=True,
        )
    except Exception as e:
        print(e)


def prompt():
    sopa_dir = Path(__file__).parents[2]
    workflow_dir = sopa_dir / "workflow"
    env_dict = dotenv_values(sopa_dir / ".env")

    data_dir = Path(env_dict["DATA_PATH"])
    cold_data_dir = Path(env_dict["COLD_STORAGE_DATA_PATH"])

    tissue = inquirer.fuzzy(message="Select a tissue:", choices=search(cold_data_dir)).execute()

    slide = inquirer.fuzzy(
        message="Select a slide:", choices=search(cold_data_dir / tissue)
    ).execute()

    region_name = inquirer.fuzzy(
        message="Select a region:", choices=search(cold_data_dir / tissue / slide)
    ).execute()

    data_path = data_dir / Path(tissue) / slide / region_name

    if inquirer.confirm(
        message="Choose among existing an existing config?", default=True
    ).execute():
        config_dir = inquirer.fuzzy(
            message="First, select the technology associated to the config:",
            choices=search(workflow_dir / "config"),
        ).execute()

        config_path = inquirer.fuzzy(
            message="Select a config:",
            choices=search(
                workflow_dir / "config" / config_dir, is_dir=False, suffix=".yaml", return_path=True
            ),
        ).execute()
    else:
        config_path = inquirer.text(
            message="Write the absolute path to your YAML config file:"
        ).execute()

        assert Path(config_path).exists(), f"File {config_path} is not existing"

    suffix = inquirer.text(
        message="Add a suffix to your data directory name (left empty for default):"
    ).execute()

    if inquirer.confirm(message="Confirm? This will run the whole pipeline").execute():
        run(data_path, config_path, suffix)


def main():
    try:
        return prompt()
    except (KeyboardInterrupt, ValueError, AssertionError) as e:
        print(e)
        try:
            if inquirer.confirm(message="Restart prompt?").execute():
                return main()
        except KeyboardInterrupt:
            print("Exiting")


if __name__ == "__main__":
    main()
