"""
A flexable config module built around configparser.

 * Reference options by using dotted notation (config.option1)
 * Config becomes accessible globally simply by importing config anywhere
        so... anywhere you import config, you should be able to
        print(config.option1)
 * partial support for json config files.

"""
# Usage:
# In a project at root you should
#   import config
#   config.init('/path/to/config.conf', 'DEFAULT')
#
# In plugins or other areas of a project you could
#   import config
#   local_config = config.LocalConfig('/path/to/config.conf', 'DEFAULT')
#
# Then in that plugin or wherever
#   config.option1
#   local_config.option1


import configparser
import json
import pathlib
import sys

class LocalConfig(object):
    """Creates a config object but not incorporated into the global module."""
    def __init__(self, config_file, section='DEFAULT'):
        _build_attributes(config_file, section, self)

    def append(self, config_file, section='DEFAULT'):
        """Add additional items from other config files to our config object."""
        _build_attributes(config_file, section, self)

    def get_boolean(self, value):
        attribute = getattr(self, value)
        # It's possibe for the program to modify a config value at runtime,
        #   and it may not set as an actual boolean instead of a string.
        if type(attribute) == bool:
            return attribute
        if attribute and attribute.lower() in ['yes', 'true', 'on', '1']:
            return True
        return False

    def __getattr__(self, item):
        """Always return None if an attribute does not exist."""
        # Config values are only available as all lower case. Try lower().
        return self.__dict__.get(item.lower(), None)

def _build_attributes_configparser(config_file, section, target):
    """Parses a config section and sets attributes to an object.

    Arguments:
        config_file - the config file to open and pull
        section     - the config file section to build
        target      - the object to which attributes should be set
    """
    _config = configparser.ConfigParser()
    _config.read(config_file)

    for k,v in _config[section].items():
        try:
            v = int(v)
        except:
            pass
        setattr(target, k, v)

def _build_attributes_json(config_file, target):
    """Parses a json as config and sets attributes to an object.

    Arguments:
        config_file - the config file to open and pull
        target      - the object to which attributes should be set
    """
    with open(config_file, 'r') as fin:
        _config = json.load(fin)

    for k,v in _config.items():
        try: k = int(k)
        except: pass
        try: v = int(v)
        except: pass

        # We should be recursively converting dictionaries into objects here
        #   so you can config.section.option. Combine with some of the database
        #   classes I've made in the past to make them accessible any way you
        #   prefer.
        setattr(target, k, v)

def init(config_file, section='DEFAULT'):
    # Pull values from our config file; flatten them into our object
    module = sys.modules[__name__]

    # This could be better with a function to identify the config file type
    #   branching with a dictionary-switch.
    if pathlib.Path(config_file).suffix ==  '.json':
        _build_attributes_json(config_file, module)
    else:
        _build_attributes(config_file, section, module)
    return module

def get_boolean(value):
    module = sys.modules[__name__]
    attribute = getattr(module, value)
    if type(attribute) == bool:
        # It's possibe for the program to modify a config value at runtime,
        #   and it may not set as an actual boolean instead of a string.
        return attribute
    if attribute and attribute.lower() in ['yes', 'true', 'on', '1']:
        return True
    return False

def get(value, default = None):
    module = sys.modules[__name__]
    return getattr(module, value, default)

# Project-specific processed config goes below here
# e.g. option1 = os.path.whatver(processed_values)
