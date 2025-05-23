import json
import os

from .log import PluginLog

class _PluginMetadata(PluginLog):

    def __init__(self):
        super().__init__()
        self._metadata_filename = "metadata.json"
        self._metadata = {}

        self._name = None
        self._version = "1.0 (from loader)"
    
    def _load_plugin_metadata(self, folder_name: str, path: str, files: list):
        """
        Load metadata from the plugin folder
        :param folder_name: Name of the plugin folder
        :param path: Path to the plugin folder
        :param files: List of files in the plugin folder
        :return: None
        """

        self._metadata[folder_name] = {}

        if self._metadata_filename in files:
            self.log("debug", f"Loading {self._metadata_filename} from {folder_name} plugin...")

            with open(os.path.join(path, self._metadata_filename), "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)

                    if data:
                        core_data = data.get("plugin_metadata")

                        if core_data is None:
                            self.log("debug", f"{self._metadata_filename} in plugin {folder_name} is empty.")
                            return None

                        self._metadata[folder_name]["name"] = core_data["name"]
                        self._metadata[folder_name]["version"] = core_data["version"]

                        self.log("debug", f"✅ {self._metadata_filename} from {self._metadata[folder_name]["name"]} ({folder_name}) was loaded successfully")
                except json.JSONDecodeError as e:
                    self.log("error", f"Something was happened: {e}")
        else:
            # Write standard data to self.self._metadata
            self._metadata[folder_name]["name"] = folder_name
            self._metadata[folder_name]["version"] = self._version

            self.log("warning", f"⚠️ {self._metadata_filename} is missing in the plugin {self._metadata[folder_name]["name"]}. " \
                f"Standard data was written to self._metadata: {self._metadata[folder_name]}")

    def get_metadata(self, folder_name: str) -> dict:
        """
        Get metadata of the plugin by folder name
        :param folder_name: Name of the plugin folder
        :return: Metadata of the plugin
        """

        if folder_name in self._metadata:
            return self._metadata[folder_name]
        else:
            self.log("error", f"❌ The plugin {folder_name} is not loaded")
            return None
