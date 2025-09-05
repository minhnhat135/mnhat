import json
import base64
from .md5 import calculate_md5_b64
from .x64hash import x64hash128

class RiskData:
    def __init__(self, user_agent, language, color_depth, device_memory, hardware_concurrency, width, height, avail_width, avail_height, timezone_offset, timezone, platform):
        self.user_agent = user_agent
        self.language = language
        self.color_depth = color_depth
        self.device_memory = device_memory
        self.hardware_concurrency = hardware_concurrency
        self.width = width
        self.height = height
        self.avail_width = avail_width
        self.avail_height = avail_height
        self.timezone_offset = timezone_offset
        self.timezone = timezone
        self.platform = platform

    def generate(self):
        data = {
            "version": "1.0.0",
            "deviceFingerprint": self.df_value(),
            "persistentCookie": [],
            "components": self.generate_components()
        }
        return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

    def df_value(self):
        return f"{self.generate_fingerprint()}:40"

    def generate_components(self):
        # Simplified components list
        components = [
            {"key": "userAgent", "value": self.user_agent},
            {"key": "language", "value": self.language},
            {"key": "colorDepth", "value": self.color_depth},
            #... add other components as needed
        ]
        return self.process_dfp_components(components)

    def process_dfp_components(self, components):
        parsed_components = {}
        for comp in components:
            key, val = comp['key'], comp['value']
            # Simplified logic from JS
            if isinstance(val, (int, float)) or key in ["timezone", "language", "platform"]:
                 parsed_components[key] = val
            elif isinstance(val, str):
                 parsed_components[key] = x64hash128(val)
        return parsed_components

    def pad_string(self, f, e):
        if len(f) >= e:
            return f[:e]
        return '0' * (e - len(f)) + f

    def generate_fingerprint(self):
        # This is a very simplified version of the JS fingerprint generation
        plugins_str = "Plugin 0: Chrome PDF Viewer..." # The full string from JS
        plugins_md5 = calculate_md5_b64(plugins_str)
        
        user_agent_md5 = calculate_md5_b64(self.user_agent)

        fingerprint = self.pad_string(plugins_md5, 10) + self.pad_string(user_agent_md5, 10)
        return fingerprint.replace('+', 'G').replace('/', 'D')