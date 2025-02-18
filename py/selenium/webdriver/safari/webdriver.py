# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import http.client as http_client


import warnings

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from .options import Options
from .service import Service
from .remote_connection import SafariRemoteConnection

DEFAULT_EXECUTABLE_PATH = "/usr/bin/safaridriver"
DEFAULT_SAFARI_CAPS = DesiredCapabilities.SAFARI.copy()


class WebDriver(RemoteWebDriver):
    """
    Controls the SafariDriver and allows you to drive the browser.

    """

    def __init__(self, port=0, executable_path=DEFAULT_EXECUTABLE_PATH, reuse_service=False,
                 desired_capabilities=DEFAULT_SAFARI_CAPS, quiet=False,
                 keep_alive=True, service_args=None, options: Options = None, service: Service = None):
        """

        Creates a new Safari driver instance and launches or finds a running safaridriver service.

        :Args:
         - port - The port on which the safaridriver service should listen for new connections. If zero, a free port will be found.
         - executable_path - Path to a custom safaridriver executable to be used. If absent, /usr/bin/safaridriver is used.
         - reuse_service - If True, do not spawn a safaridriver instance; instead, connect to an already-running service that was launched externally.
         - desired_capabilities: Dictionary object with desired capabilities (Can be used to provide various Safari switches).
         - quiet - If True, the driver's stdout and stderr is suppressed.
         - keep_alive - Whether to configure SafariRemoteConnection to use
             HTTP keep-alive. Defaults to True.
         - service_args : List of args to pass to the safaridriver service
         - service - Service object for handling the browser driver if you need to pass extra details
        """
        if port:
            warnings.warn("port has been deprecated, please set it via the service class",
                          DeprecationWarning, stacklevel=2)

        if executable_path != DEFAULT_EXECUTABLE_PATH:
            warnings.warn("executable_path has been deprecated, please use the Options class to set it",
                          DeprecationWarning, stacklevel=2)
        if reuse_service:
            warnings.warn("reuse_service has been deprecated, please use the Service class to set it",
                          DeprecationWarning, stacklevel=2)
        if desired_capabilities != DEFAULT_SAFARI_CAPS:
            warnings.warn("desired_capabilities has been deprecated, please use the Options class to set it",
                          DeprecationWarning, stacklevel=2)
        if quiet:
            warnings.warn("quiet has been deprecated, please use the Service class to set it",
                          DeprecationWarning, stacklevel=2)
        if not keep_alive:
            warnings.warn("keep_alive has been deprecated, please use the Service class to set it",
                          DeprecationWarning, stacklevel=2)

        if service_args:
            warnings.warn("service_args has been deprecated, please use the Service class to set it",
                          DeprecationWarning, stacklevel=2)

        self._reuse_service = reuse_service
        if service:
            self.service = service
        else:
            self.service = Service(executable_path, port=port, quiet=quiet, service_args=service_args)
        if not reuse_service:
            self.service.start()

        executor = SafariRemoteConnection(remote_server_addr=self.service.service_url,
                                          keep_alive=keep_alive)

        RemoteWebDriver.__init__(
            self,
            command_executor=executor,
            desired_capabilities=desired_capabilities)

        self._is_remote = False

    def quit(self):
        """
        Closes the browser and shuts down the SafariDriver executable
        that is started when starting the SafariDriver
        """
        try:
            RemoteWebDriver.quit(self)
        except http_client.BadStatusLine:
            pass
        finally:
            if not self._reuse_service:
                self.service.stop()

    # safaridriver extension commands. The canonical command support matrix is here:
    # https://developer.apple.com/library/content/documentation/NetworkingInternetWeb/Conceptual/WebDriverEndpointDoc/Commands/Commands.html

    # First available in Safari 11.1 and Safari Technology Preview 41.
    def set_permission(self, permission, value):
        if not isinstance(value, bool):
            raise WebDriverException("Value of a session permission must be set to True or False.")

        payload = {}
        payload[permission] = value
        self.execute("SET_PERMISSIONS", {"permissions": payload})

    # First available in Safari 11.1 and Safari Technology Preview 41.
    def get_permission(self, permission):
        payload = self.execute("GET_PERMISSIONS")["value"]
        permissions = payload["permissions"]
        if not permissions:
            return None

        if permission not in permissions:
            return None

        value = permissions[permission]
        if not isinstance(value, bool):
            return None

        return value

    # First available in Safari 11.1 and Safari Technology Preview 42.
    def debug(self):
        self.execute("ATTACH_DEBUGGER")
        self.execute_script("debugger;")
