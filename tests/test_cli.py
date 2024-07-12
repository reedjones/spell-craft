import unittest
from pathlib import Path
from spell_craft.cli import load_commands, load_configuration, create_cli_from_commands

import os


print(os.getcwd())

assert os.path.isfile("spell_craft/plugins/echo_str/commands.txt")


class TestCLIGenerator(unittest.TestCase):

    def setUp(self):
        # Define paths to test commands and configurations
        self.list_files_commands_path = Path(
            "spell_craft/plugins/list_files/commands.txt"
        )
        self.list_files_config_path = Path(
            "spell_craft/plugins/list_files/commands.json"
        )
        self.echo_str_commands_path = Path("spell_craft/plugins/echo_str/commands.txt")
        self.echo_str_config_path = Path("spell_craft/plugins/echo_str/commands.yaml")

    def test_load_commands(self):
        commands = load_commands(self.list_files_commands_path)
        self.assertEqual(len(commands), 1)
        self.assertIn("list_files:ls -la {{ directory }}", commands)

    def test_load_configuration_json(self):
        config = load_configuration(self.list_files_config_path)
        self.assertIsInstance(config, dict)
        self.assertIn("list_files", config)
        self.assertIn("arguments", config["list_files"])
        self.assertIn("directory", config["list_files"]["arguments"])

    def test_load_configuration_yaml(self):
        config = load_configuration(self.echo_str_config_path)
        self.assertIsInstance(config, dict)
        self.assertIn("echo_str", config)
        self.assertIn("arguments", config["echo_str"])
        self.assertIn("message", config["echo_str"]["arguments"])

    def test_create_cli_from_commands_list_files(self):
        commands = load_commands(self.list_files_commands_path)
        config = load_configuration(self.list_files_config_path)
        plugin_app = DummyTyperApp()

        create_cli_from_commands("list_files", commands, config, plugin_app)

        self.assertIn("list_files", plugin_app.commands)
        self.assertTrue(callable(plugin_app.commands["list_files"]))

    def test_create_cli_from_commands_echo_str(self):
        commands = load_commands(self.echo_str_commands_path)
        config = load_configuration(self.echo_str_config_path)
        plugin_app = DummyTyperApp()

        create_cli_from_commands("echo_str", commands, config, plugin_app)

        self.assertIn("echo_str", plugin_app.commands)
        self.assertTrue(callable(plugin_app.commands["echo_str"]))


class DummyTyperApp:
    """
    Dummy class mimicking Typer's Typer() object to capture generated CLI commands.
    """

    def __init__(self):
        self.commands = {}

    def command(self, name=None):
        def decorator(func):
            self.commands[name] = func
            return func

        return decorator


if __name__ == "__main__":
    unittest.main()
