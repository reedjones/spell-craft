import json
import yaml
import typer
from jinja2 import Template
from pathlib import Path
import subprocess
from typing import Dict

app = typer.Typer()


def run_shell_command(command: str):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode == 0:
        typer.echo(result.stdout)
    else:
        typer.echo(result.stderr)


def load_commands(file_path: Path):
    with open(file_path, "r") as file:
        commands = file.read().splitlines()
    return commands


def load_configuration(file_path: Path) -> Dict:
    with open(file_path, "r") as file:
        if file_path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(file)
        elif file_path.suffix == ".json":
            return json.load(file)
        else:
            raise ValueError("Configuration file must be .json or .yaml")


def create_cli_from_commands(
    plugin_name: str, commands, configuration, plugin_app: typer.Typer
):
    for command in commands:
        command_template = Template(command)
        command_name = command.split(":", 1)[0]
        command_details = configuration.get(command_name, {})

        def cli_command(**kwargs):
            command_rendered = command_template.render(kwargs)
            run_shell_command(command_rendered)

        cli_command.__annotations__ = {
            key: str for key in command_details.get("arguments", {}).keys()
        }
        cli_command.__name__ = command_name

        plugin_app.command(name=command_name)(cli_command)


def load_plugins(plugins_dir: Path):
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir():
            commands_file = plugin_dir / "commands.txt"
            config_file = next(plugin_dir.glob("commands.*"), None)
            if commands_file.exists() and config_file:
                commands = load_commands(commands_file)
                configuration = load_configuration(config_file)

                plugin_app = typer.Typer()
                app.add_typer(plugin_app, name=plugin_dir.name)

                create_cli_from_commands(
                    plugin_dir.name, commands, configuration, plugin_app
                )


@app.command()
def generate_cli(plugins_dir: Path):
    load_plugins(plugins_dir)
    app()


if __name__ == "__main__":
    app()
