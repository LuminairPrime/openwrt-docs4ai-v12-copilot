# luci-examples Navigation Map

> **Contains:** Headers and function signatures for luci-examples.
> **Generated:** 2026-03-28T08:27:16.398522+00:00

---

> **Summary:** The `commands.js` module in the `luci-examples` application provides a web interface for configuring custom shell commands in OpenWrt. It allows users to create, modify, and delete commands, with options for adding descriptions, command lines, and custom arguments. Additionally, it includes a flag for public access, enabling commands to be executed without authentication. This module is built using JavaScript and leverages the LuCI framework for rendering forms and views.
> **Use Case:** Use this module when you need to create a user-friendly interface for managing custom shell commands in OpenWrt. It is particularly useful for applications that require command execution from a web interface.
# commands.js

> **Summary:** The `commands.uc` module in the `luci-examples` application provides functionality to parse command-line arguments and execute commands within the OpenWrt environment. It includes functions like `parse_args` for decoding strings into arguments, `parse_cmdline` for constructing command arguments from UCI configurations, and `execute_command` for running commands and capturing their output. Additionally, it handles output redirection and checks for binary data in the command output. This module is essential for applications that require dynamic command execution based on user input or configurations.
> **Use Case:** Use this module when you need to execute system commands dynamically in response to user input or configuration settings in OpenWrt applications.
# commands.uc

> **Summary:** The overview.js module is part of the luci-examples application in OpenWrt, designed to manage Dynamic DNS (DDNS) services. It provides functionality to retrieve service logs, check DDNS status, and manage service lists from various sources. Key functions include callGetLogServices, callDDnsGetStatus, and callGenServiceList, which facilitate interaction with DDNS services and their configurations. The module also handles WAN interface detection and service support validation based on user-defined settings.
> **Use Case:** Use this module when you need to manage and monitor Dynamic DNS services in an OpenWrt environment, particularly for applications requiring real-time updates and service status checks.
# overview.js

> **Summary:** The 70_ddns.js module is part of the luci-examples package in OpenWrt, designed to manage Dynamic DNS (DDNS) services through a web interface. It utilizes the RPC mechanism to fetch the status of configured DDNS services and displays this information in a structured table format. The module loads DDNS configurations using the UCI system and presents details such as the next update time, lookup hostname, registered IP address, and network type. It also handles cases where no services are configured by displaying an appropriate message.
> **Use Case:** Use this module when you need to provide a user interface for monitoring and managing Dynamic DNS services in OpenWrt. It is particularly useful for users who require real-time updates on their DDNS configurations.
# 70_ddns.js

> **Summary:** The `ddns.uc` module is designed for managing Dynamic DNS (DDNS) services within the OpenWrt environment. It provides functions for retrieving service logs, checking the status of DDNS services, and formatting dates. Key functions include `get_services_log`, which fetches logs for specified services, and `get_services_status`, which retrieves the current status of all configured DDNS services. Additionally, it includes utility functions for date formatting and calculating time intervals.
> **Use Case:** Use the `ddns.uc` module when you need to manage or monitor DDNS services in OpenWrt, particularly for logging and status checks.
# ddns.uc
#!/usr/bin/env ucode

> **Summary:** The api.js module provides a JavaScript interface for interacting with Docker through the LuCI web interface in OpenWrt. It utilizes RPC calls to fetch network interface data and UCI configurations, allowing for the dynamic determination of local IP addresses and Docker host settings. Key functions include `callNetworkInterfaceDump` for retrieving network interface details and `call_docker` for making API calls to the Docker host. Additionally, it features a helper function `processLines` to handle NDJSON or line-delimited JSON data streams.
> **Use Case:** This module is useful when you need to manage Docker containers on OpenWrt devices through a web interface. It is particularly applicable in scenarios where dynamic network configurations are involved.
# api.js

> **Summary:** The `common.js` module is part of the `luci-examples` application and provides JavaScript functions for interacting with Docker containers through the LuCI interface in OpenWrt. It includes a variety of RPC methods for managing Docker containers, such as creating, inspecting, starting, stopping, and removing containers. Additional functionalities include retrieving container logs, stats, and events, as well as Docker system information and version details. This module is designed to streamline Docker management tasks within the OpenWrt environment.
> **Use Case:** Use this module when developing a LuCI application that requires Docker container management capabilities on OpenWrt devices.
# common.js

> **Summary:** The `configuration.js` module is part of the `luci-examples` package and provides a JavaScript interface for configuring Docker settings within the LuCI web interface. It allows users to set global Docker configurations such as default flags, API version, Docker root directory, default bridge network, registry mirrors, log levels, and client connection settings. The module also includes options for configuring registry authentication for push/pull operations on custom registries. This module enhances the management of Docker containers through a user-friendly web interface.
> **Use Case:** Use this module when you need to manage Docker configurations via the LuCI interface on OpenWrt devices, particularly when dealing with Docker container management.
# configuration.js

> **Summary:** The `container.js` module is a JavaScript component for the Luci interface of OpenWrt, specifically designed for managing Docker containers. It provides functionalities to calculate memory and CPU usage percentages, utilizing helper functions like `calculateMemoryUsage` and `calculateCPUUsage` to process container statistics. The module also includes dummy data structures for testing and simulating container statistics and process information. This script is part of the `luci-app-dockerman`, which enhances the Docker management experience within the OpenWrt framework.
> **Use Case:** Use this module when integrating Docker container management into the Luci web interface of OpenWrt, particularly for monitoring resource usage of containers.
# container.js

> **Summary:** The `container_new.js` module is part of the Luci framework for managing Docker containers within OpenWrt. It provides functionality to create and configure new Docker containers, including handling duplicate container configurations. The module retrieves necessary data such as available images, networks, and volumes, and allows users to set various container parameters like name, image, network settings, and environment variables. Additionally, it reflects changes in the Docker API, such as the removal of MAC address configuration through the container's configuration fields.
> **Use Case:** Use this module when you need to create new Docker containers or duplicate existing ones in an OpenWrt environment. It is particularly useful for managing container configurations through the Luci web interface.
# container_new.js

> **Summary:** The `containers.js` module is a JavaScript component for the LuCI interface of OpenWrt that manages Docker containers. It provides functionalities to list, display, and interact with Docker containers, images, and networks on a connected Docker host. The module includes methods for loading data, rendering the user interface, and calculating container states such as running, paused, and stopped. Additionally, it allows users to prune unused containers through a button action in the UI.
> **Use Case:** Use this module when you need to manage Docker containers within the LuCI web interface on an OpenWrt device. It is particularly useful for users who want to monitor and control their Docker environment easily.
# containers.js

> **Summary:** The `events.js` module is part of the Luci Docker Manager application for OpenWrt, designed to handle Docker events and display them in a user-friendly interface. It supports fetching event data in both `application/x-ndjson` and `application/json-seq` formats, allowing for flexible content negotiation. The module includes functions to load events, render event lists, and apply filters based on event types and timestamps. Additionally, it provides a structured way to interact with Docker events through a graphical interface, enhancing usability for managing Docker containers.
> **Use Case:** Use the `events.js` module when you need to display and filter Docker events in the Luci web interface of OpenWrt. It is particularly useful for users managing Docker containers who require real-time insights into container activities.
# events.js

> **Summary:** The `images.js` module is part of the Luci Docker Manager application for OpenWrt, providing functionalities to manage Docker images through a web interface. It allows users to load and display available Docker images and containers, pull new images from a registry, and calculate the total size of images. Key functions include `load()`, which retrieves image and container lists, and `render()`, which constructs the user interface for displaying images and their details. The module also includes features for managing image tags and handling user interactions for pulling images.
> **Use Case:** Use this module when you need to manage Docker images within the OpenWrt Luci interface, particularly for pulling images from a Docker registry or viewing existing images and their sizes.
# images.js

> **Summary:** The `network.js` module is a JavaScript component designed for the Docker manager in the LuCI interface of OpenWrt. It provides functionality to inspect Docker networks and list associated containers, leveraging the `dockerman.common` library. The module includes methods for loading network details, rendering the network overview, and displaying configuration options in a structured format. It features tabs for network information and configurations, allowing users to view and manage Docker network settings effectively.
> **Use Case:** Use this module when you need to manage and inspect Docker networks within the OpenWrt LuCI interface, particularly in applications that utilize Docker containers.
# network.js

> **Summary:** The `network_new.js` module is part of the Luci application for managing Docker networks within OpenWrt. It provides a user interface for creating new Docker networks by allowing users to specify various parameters such as network name, driver type, and subnet configurations. Key functions include rendering a form with options for network properties, such as 'macvlan_mode' and 'ipvlan_mode', as well as enabling users to set labels and options for the network. This module is designed to facilitate the creation and management of Docker networks seamlessly through the OpenWrt web interface.
> **Use Case:** Use the `network_new.js` module when you need to create and configure new Docker networks in an OpenWrt environment, especially when managing containerized applications.
# network_new.js

> **Summary:** The `networks.js` module is part of the Luci interface for managing Docker networks within OpenWrt. It provides functionality to load and display a list of Docker networks and associated containers, allowing users to manage these networks through a web interface. Key functions include loading network and container data, rendering a network overview table, and handling network pruning and removal actions. The module utilizes promises for asynchronous operations and integrates with the Docker manager's common functionalities.
> **Use Case:** Use this module when you need to manage Docker networks through the Luci web interface in OpenWrt, particularly for viewing, creating, or removing networks.
# networks.js

> **Summary:** The `overview.js` module is part of the `luci-examples` application for managing Docker containers through the LuCI interface in OpenWrt. It provides functions to retrieve sets of image IDs, network IDs, and volume mountpoints currently in use by Docker containers. Key functions include `getImagesInUseByContainers`, `getNetworksInUseByContainers`, and `getVolumesInUseByContainers`, which process container objects to extract relevant information. The module also handles loading Docker-related data and executing actions on containers through the `handleAction` method.
> **Use Case:** Use this module when you need to display an overview of Docker container usage and manage container actions within the LuCI web interface on OpenWrt.
# overview.js

> **Summary:** The `volumes.js` module is part of the Luci application for managing Docker containers in OpenWrt. It provides functionality to list, create, and prune Docker volumes through a user-friendly interface. The module utilizes promises to load volume and container data asynchronously, and it includes features for rendering this data in a structured format. Additionally, it allows users to perform actions such as creating new volumes and pruning unused ones directly from the UI.
> **Use Case:** Use this module when you need to manage Docker volumes on an OpenWrt device running the Luci interface. It is particularly useful for users looking to maintain their Docker environment efficiently.
# volumes.js

> **Summary:** The `docker_rpc.uc` module provides an interface for interacting with Docker's API using ucode in OpenWrt. It includes functions for handling HTTP requests, reading chunked responses, and managing Docker socket connections. Key functions include `call_docker`, which facilitates API calls to Docker, and `get_api_ver`, which retrieves the current API version from the configuration. The module is designed to work with Docker's v1.47 API and supports both local and remote socket connections.
> **Use Case:** Use this module when you need to integrate Docker functionality into your OpenWrt applications, particularly for managing containers and images through the Docker API.
# docker_rpc.uc
#!/usr/bin/env ucode

> **Summary:** The `docker.uc` module provides a Docker HTTP streaming endpoint for handling file uploads and streaming responses in OpenWrt applications. It includes functions for managing chunked file transfers, building HTTP headers, parsing initial HTTP responses, and streaming response chunks from a socket. Additionally, it offers capabilities to send HTTP 200 OK responses and generate debug output when needed. This module is built against the Docker v1.47 API and is useful for integrating Docker functionalities into OpenWrt's Luci framework.
> **Use Case:** Use the `docker.uc` module when you need to implement Docker container management features within an OpenWrt web interface. It is particularly useful for applications that require file uploads or streaming data from Docker containers.
# docker.uc

> **Summary:** The `docker_socket.uc` module provides functions to retrieve the Docker socket path from UCI configuration in OpenWrt, ensuring backward compatibility. It includes two main functions: `get_socket_dest_compat`, which returns a socket address structure compatible with various protocols, and `get_socket_dest`, which simply retrieves the socket path as a string. The module supports both Unix and TCP/UDP socket formats, adapting to different configurations. It also handles IPv4 and IPv6 addresses, extracting the necessary details from the provided socket path.
> **Use Case:** Use this module when you need to obtain the Docker socket path in OpenWrt applications, particularly when working with Docker configurations that may vary in format.
# docker_socket.uc

> **Summary:** The `form.js` module is a JavaScript file used in the LuCI framework for creating a user interface form that interacts with UCI configuration files in OpenWrt. It defines a form structure that includes multiple sections and various input types, such as text fields, flags, and dynamic lists. The form is mapped to a configuration file named 'example' located at `/etc/config/example`, allowing users to read and write configuration settings. Each section can contain different types of options, including a password input and a select dropdown with predefined values.
> **Use Case:** Use this module when you need to create a custom configuration form in a LuCI application that interacts with UCI settings in OpenWrt.
# form.js

> **Summary:** The `htmlview.js` module is a JavaScript component for the LuCI framework in OpenWrt, designed to create a dynamic HTML view based on UCI configuration data. It includes functions for loading UCI configurations, rendering HTML elements, and displaying specific configuration options. The `load` function retrieves the 'example' configuration, while the `render` function constructs an HTML structure that presents the configuration data. This module is particularly useful for developers looking to create custom web interfaces for managing OpenWrt settings.
> **Use Case:** Use `htmlview.js` when you need to build a web interface that displays and interacts with UCI configuration data in OpenWrt.
# htmlview.js

> **Summary:** The `rpc.js` module in the `luci-examples` application provides a framework for making Remote Procedure Calls (RPC) to the LuCI interface. It defines RPC calls using the `rpc.declare` method, which allows interaction with backend services through defined methods like `get_sample1` and `get_sample3`. The module includes error handling for RPC responses and renders data in a structured format using DOM manipulation. Additionally, it demonstrates how to load data asynchronously and display it in a user-friendly manner.
> **Use Case:** Use this module when you need to implement RPC calls in a LuCI application to interact with backend services and display the results in a web interface.
# rpc.js

> **Summary:** The `rpc-jsonmap-tablesection.js` module is a JavaScript example for LuCI that demonstrates how to create a view using a JSONMap to display data retrieved via RPC calls. It defines an RPC call to fetch sample data and utilizes the LuCI form API to render this data in a structured format. The module includes error handling for RPC failures and sets up a read-only form with a tabbed display for better organization. Additionally, it provides a mechanism to capitalize option names and dynamically list items, enhancing the user interface experience.
> **Use Case:** Use this module when you need to present data from an RPC call in a structured, read-only format within the LuCI web interface. It is particularly useful for displaying configuration data that should not be modified directly by the user.
# rpc-jsonmap-tablesection.js

> **Summary:** The `rpc-jsonmap-typedsection.js` module is a LuCI example that demonstrates how to create a read-only configuration form using JSON data from an RPC call. It utilizes the `rpc` and `form` libraries to define an RPC method, `get_sample2`, and to render a structured form based on the retrieved JSON data. The module includes functions for error handling and rendering the form with typed sections and options. It is designed to be used with LuCI's JSONMap for displaying configuration data in a user-friendly manner.
> **Use Case:** This module is useful when you need to display configuration data from an RPC source in a structured format within the LuCI interface, particularly when the data is read-only.
# rpc-jsonmap-typedsection.js

> **Summary:** The `example.uc` module provides a simple interface for accessing configuration data using the UCI (Unified Configuration Interface) in OpenWrt. It defines two methods: `get_sample1`, which retrieves the number of cats, dogs, and parakeets from the 'example' configuration, and `get_sample2`, which returns predefined string and numeric values along with arrays of parakeets. This module leverages the `cursor` API to interact with UCI without directly parsing configuration files. It is designed to facilitate easy data retrieval for applications built on the LuCI framework.
> **Use Case:** Use this module when you need to access and manipulate configuration data in OpenWrt applications, particularly within the LuCI web interface.
# example.uc
#!/usr/bin/env ucode
