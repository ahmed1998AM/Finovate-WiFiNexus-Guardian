"""
Plugin Manager - Manages plugin system with sandbox support
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional


class Plugin:
    """Base plugin class"""
    
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.is_active = False
        
    def activate(self) -> bool:
        """Activate the plugin"""
        self.is_active = True
        return True
    
    def deactivate(self) -> bool:
        """Deactivate the plugin"""
        self.is_active = False
        return True
    
    def execute(self, *args, **kwargs):
        """Execute plugin functionality (override in subclasses)"""
        raise NotImplementedError


class PluginManager:
    """Manages plugin lifecycle and sandboxing"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dir = None
        self.sandbox_enabled = True
        
    def initialize(self, plugin_dir: str = "plugins") -> bool:
        """Initialize plugin manager"""
        try:
            self.plugin_dir = Path(__file__).parent.parent / plugin_dir
            self.plugin_dir.mkdir(exist_ok=True)
            
            # Create example plugin directory structure
            examples_dir = self.plugin_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Plugin manager initialization error: {e}")
            return False
    
    def load_plugins(self) -> int:
        """Load all plugins from plugin directory"""
        if not self.plugin_dir:
            self.initialize()
            
        loaded_count = 0
        
        # Scan for plugin directories
        for item in self.plugin_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                plugin_file = item / "plugin.py"
                manifest_file = item / "manifest.json"
                
                if plugin_file.exists() and manifest_file.exists():
                    try:
                        plugin = self._load_plugin(item, plugin_file, manifest_file)
                        if plugin:
                            self.plugins[item.name] = plugin
                            loaded_count += 1
                    except Exception as e:
                        print(f"Error loading plugin {item.name}: {e}")
                        
        return loaded_count
    
    def _load_plugin(self, plugin_path: Path, plugin_file: Path, manifest_file: Path) -> Optional[Plugin]:
        """Load a single plugin"""
        try:
            # Load manifest
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Create plugin instance
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_path.name}",
                plugin_file
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get plugin class if exists
                if hasattr(module, 'PluginClass'):
                    plugin = module.PluginClass(
                        name=manifest.get('name', plugin_path.name),
                        version=manifest.get('version', '1.0.0'),
                        description=manifest.get('description', '')
                    )
                    return plugin
                    
        except Exception as e:
            print(f"Error loading plugin from {plugin_path}: {e}")
            
        return None
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def activate_plugin(self, name: str) -> bool:
        """Activate a plugin"""
        plugin = self.get_plugin(name)
        if plugin:
            return plugin.activate()
        return False
    
    def deactivate_plugin(self, name: str) -> bool:
        """Deactivate a plugin"""
        plugin = self.get_plugin(name)
        if plugin:
            return plugin.deactivate()
        return False
    
    def list_plugins(self) -> List[Dict]:
        """List all loaded plugins"""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "active": plugin.is_active
            }
            for plugin in self.plugins.values()
        ]
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin"""
        if name in self.plugins:
            plugin = self.plugins[name]
            plugin.deactivate()
            del self.plugins[name]
            return True
        return False
    
    def create_plugin_template(self, plugin_name: str) -> Path:
        """Create a plugin template for developers"""
        plugin_path = self.plugin_dir / plugin_name
        
        if plugin_path.exists():
            raise ValueError(f"Plugin {plugin_name} already exists")
        
        plugin_path.mkdir(parents=True)
        
        # Create manifest
        manifest = {
            "name": plugin_name,
            "version": "1.0.0",
            "description": "Custom WiFiNexus Guardian plugin",
            "author": "Developer",
            "api_version": "1.0.0"
        }
        
        with open(plugin_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create plugin template
        plugin_code = '''"""
{plugin_name} - Custom WiFiNexus Guardian Plugin
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class PluginClass:
    """Plugin implementation class"""
    
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.is_active = False
        
    def activate(self) -> bool:
        """Called when plugin is activated"""
        print(f"[{self.name}] Plugin activated")
        self.is_active = True
        return True
    
    def deactivate(self) -> bool:
        """Called when plugin is deactivated"""
        print(f"[{self.name}] Plugin deactivated")
        self.is_active = False
        return True
    
    def execute(self, *args, **kwargs):
        """Main plugin execution method"""
        if not self.is_active:
            raise RuntimeError("Plugin must be activated before use")
        
        # Plugin logic goes here
        result = {{
            "status": "success",
            "message": f"{{self.name}} executed successfully"
        }}
        
        return result
'''.format(plugin_name=plugin_name)
        
        with open(plugin_path / "plugin.py", 'w') as f:
            f.write(plugin_code)
        
        # Create README
        readme = f'''# {plugin_name}

A custom plugin for WiFiNexus Guardian.

## Installation

This plugin is already installed in the plugins directory.

## Usage

The plugin will be automatically loaded when WiFiNexus Guardian starts.

## Development

Edit `plugin.py` to implement your custom functionality.
Make sure to follow the plugin API guidelines.

## License

© 2025 Ahmed Mostafa Ibrahim - Finovate
'''
        
        with open(plugin_path / "README.md", 'w') as f:
            f.write(readme)
        
        return plugin_path
    
    def get_sandbox_status(self) -> bool:
        """Get sandbox status"""
        return self.sandbox_enabled
    
    def set_sandbox_status(self, enabled: bool):
        """Enable or disable sandbox mode"""
        self.sandbox_enabled = enabled
    
    def shutdown(self):
        """Shutdown plugin manager and deactivate all plugins"""
        for plugin in self.plugins.values():
            plugin.deactivate()
        self.plugins.clear()
