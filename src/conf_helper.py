import yaml
from box import Box

from pathlib import Path

class CovidConf:
    """
    Confiugration file object for Covid model
    This is used to easily get and set parameters as key-value pairs
    """

    def __init__(
        self,
        project_dir: str,
        config_file: str,
        config_dir=None,
    ) -> None:
        """
        Create a new CovidConf
        """

        self.project_dir = Path(project_dir)
        if config_dir:
            self.config_dir = self.project_dir / config_dir
        else:
            self.config_dir = self.project_dir / "config"

        config_file_path = self.config_dir / config_file
        config_key_val = read_config(config_file_path.as_posix())

        if config_key_val:
            self.__dict__.update(config_key_val)
            # Make the object subscriptable (so one can use conf object like a dictionary)
            self.CovidConf = self.__dict__
        else:
            print("No parameters set for CovidConf")
    
    def __getitem__(self, item):
        return self.CovidConf[item]
    
def read_config(config_file: str) -> Box:

    if config_file.endswith(".yaml"):
        with open(config_file, "r", encoding="UTF-8") as param_file:
            params = yaml.safe_load(param_file)
        
        return Box(params)
    else:
        print("The configuration file provided is not a YAML file. Please check if the file has extension '.yaml'. Exiting")
        return None