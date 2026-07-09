import importlib
import os
import sys

from database import Database
from utils.logger import logger

db = Database()
_loaded_plugins: dict = {}
PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")


def discover_plugins() -> list:
    if not os.path.isdir(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR, exist_ok=True)
        return []
    return [d for d in os.listdir(PLUGIN_DIR)
            if os.path.isdir(os.path.join(PLUGIN_DIR, d))
            and os.path.isfile(os.path.join(PLUGIN_DIR, d, "plugin.py"))]


def load_plugin(plugin_name: str) -> bool:
    if plugin_name in _loaded_plugins:
        logger.warning(f"Plugin {plugin_name} already loaded")
        return False

    plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
    if not os.path.isdir(plugin_path):
        logger.error(f"Plugin {plugin_name} not found")
        return False

    sys.path.insert(0, plugin_path)
    try:
        module = importlib.import_module(f"{plugin_name}.plugin")
        if hasattr(module, "setup"):
            module.setup()
        _loaded_plugins[plugin_name] = module
        logger.info(f"Plugin {plugin_name} loaded")
        return True
    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_name}: {e}")
        return False


def unload_plugin(plugin_name: str) -> bool:
    if plugin_name not in _loaded_plugins:
        logger.warning(f"Plugin {plugin_name} not loaded")
        return False

    try:
        module = _loaded_plugins[plugin_name]
        if hasattr(module, "teardown"):
            module.teardown()
        del _loaded_plugins[plugin_name]
        for key in list(sys.modules.keys()):
            if plugin_name in key:
                del sys.modules[key]
        logger.info(f"Plugin {plugin_name} unloaded")
        return True
    except Exception as e:
        logger.error(f"Failed to unload plugin {plugin_name}: {e}")
        return False


def reload_plugin(plugin_name: str) -> bool:
    unload_plugin(plugin_name)
    return load_plugin(plugin_name)


def list_loaded_plugins() -> list:
    return list(_loaded_plugins.keys())


async def register_plugin_meta(name: str, version: str, description: str, dependencies: list = None):
    await db.register_plugin_meta(name, version, description, dependencies or [])


async def is_plugin_enabled(plugin_name: str) -> bool:
    return await db.is_plugin_enabled(plugin_name)
