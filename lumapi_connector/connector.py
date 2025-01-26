# lumapi_connector automates connection to the Lumerical Python API.
#
# Copyright (c) 2025 Pavel Pleskunov.
# 
# lumapi_connector is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# lumapi_connector is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

from pathlib import WindowsPath
import os
import re
import sys

class MyPath(WindowsPath):
    def as_str(self):
        """ Returns the path converted to a string. """
        return str(self)

class LumAPI():
    def __init__(self, endpoint = "C:\\Program Files\\Lumerical"):
        """ Detect the available version and initialize the Lumerical API. """

        self.endpoint = MyPath(endpoint)
        self.version_subdir_pattern = re.compile(r"^v(\d{3})$")
        
        self.api_version = self._get_api_version()
        if self.api_version is None:
            raise FileNotFoundError("Unable to detect Lumerical API on the system!")

        # Update the endpoint to include the detected API version
        self.endpoint = self.endpoint / self.api_version / "api" / "python"

    def connect(self):
        print(f"Detected Lumerical API version: {self.api_version}. Conecting...")
        paths = [self.endpoint.as_str(), os.path.dirname(__file__)]
        for path in paths:
            if path not in sys.path:
                sys.path.append(path)

            import lumapi # type: ignore
            print("Conected.")
            return lumapi

    def _get_api_version(self):
        """ Retrieve the latest available API version. """
        versions_available = []

        try:
            # List all subdirectories in the endpoint
            subdirs = [MyPath(self.endpoint / subdir) for subdir in os.listdir(self.endpoint)]

            for subdir in subdirs:
                match = self.version_subdir_pattern.match(subdir.name)
                if match and subdir.is_dir():
                    versions_available.append(int(match.group(1)))

            if versions_available:
                latest = max(versions_available)
                return f"v{latest:03d}"
            else:
                print("No API subdirectories found!")
                return None

        except FileNotFoundError:
            print(f"The directory '{self.endpoint.as_str()}' does not exist.")
            return None

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None