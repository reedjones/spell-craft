# type: ignore[attr-defined]
from typing import Optional

from enum import Enum
from random import choice

import typer
from rich.console import Console

from spell_craft import version
from spell_craft.example import hello


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


app = typer.Typer(
    name="spell-craft",
    help="SpellCraft CLI is a Python project that generates command-line interfaces (CLIs) from configurations. Each CLI plugin is packaged as a separate module containing a configuration and a list of commands. Our nomenclature revolves around the concept of spells and incantations, where plugins are spells and commands are incantations.",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]spell-craft[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command(name="")
def main(
    name: str = typer.Option(..., help="Person to greet."),
    color: Optional[Color] = typer.Option(
        None,
        "-c",
        "--color",
        "--colour",
        case_sensitive=False,
        help="Color for print. If not specified then choice will be random.",
    ),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the spell-craft package.",
    ),
) -> None:
    """Print a greeting with a giving name."""
    if color is None:
        color = choice(list(Color))

    greeting: str = hello(name)
    console.print(f"[bold {color}]{greeting}[/]")


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


if __name__ == "__main__":
    app()
