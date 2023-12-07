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


def search(path: Path, is_dir: Optional[bool] = True, suffix: Optional[str] = None) -> List[Path]:
    choices = [p.name for p in sorted(list(path.iterdir())) if is_valid(p, is_dir, suffix)]

    if not choices:
        raise ValueError(f"No valid file/subdirectory inside {path}")
    return choices


def run(relative_region, region, config):
    (region / "images").mkdir(parents=True, exist_ok=True)

    print(f"Starting pipeline... (you can exit with ctrl+a+d)")
    try:
        subprocess.run(
            f"""snakemake --config region={relative_region} config={config} --profile slurm --rerun-triggers mtime params input code""",
            shell=True,
            check=True,
        )
    except Exception as e:
        print(e)


def parse_history(history):
    with open(history, "r") as f:
        return [line.split() for line in f.readlines()]


def prompt():
    sopa_dir = Path(__file__).parents[2]
    workflow_dir = sopa_dir / "workflow"
    env_dict = dotenv_values(sopa_dir / ".env")

    data_path = Path(env_dict["DATA_PATH"])
    cold_data_path = Path(env_dict["COLD_STORAGE_DATA_PATH"])
    history_path = Path(env_dict["MERFISH"]) / ".smk_history"

    tissue = inquirer.fuzzy(message="Select a tissue:", choices=search(cold_data_path)).execute()

    slide = inquirer.fuzzy(
        message="Select a slide:", choices=search(cold_data_path / tissue)
    ).execute()

    region_name = inquirer.fuzzy(
        message="Select a region:", choices=search(cold_data_path / tissue / slide)
    ).execute()

    relative_region = Path(tissue) / slide / region_name
    region = data_path / relative_region
    history = history_path / f"{tissue}_{slide}_{region_name}.txt"

    if history.exists():
        last_config, *_ = parse_history(history)[-1]
        if inquirer.confirm(
            message=f"A pipeline has already been run on this region. Run again with config='{last_config}'?"
        ).execute():
            return run(relative_region, region, last_config)

    (workflow_dir / "config" / tissue).mkdir(exist_ok=True)
    config = inquirer.fuzzy(
        message="Select a project config:",
        choices=search(workflow_dir / "config" / tissue, is_dir=False, suffix=".toml"),
    ).execute()

    if inquirer.confirm(message="Confirm? This will run the whole pipeline").execute():
        run(relative_region, region, config)


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
