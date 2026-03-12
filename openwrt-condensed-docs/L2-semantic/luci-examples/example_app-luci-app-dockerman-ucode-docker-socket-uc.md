---
title: docker_socket.uc
module: luci-examples
origin_type: example_app
token_count: 724
version: 3da0ac5
source_file: L1-raw/luci-examples/example_app-luci-app-dockerman-ucode-docker-socket-uc.md
last_pipeline_run: '2026-03-12T13:29:57.345766+00:00'
upstream_path: applications/luci-app-dockerman/ucode/docker_socket.uc
language: ucode
ai_summary: 'The `docker_socket.uc` module provides functions to retrieve the Docker socket path from UCI configuration in OpenWrt, ensuring backward compatibility. It includes two main functions: `get_socket_dest_compat`, which returns a socket address structure compatible with various protocols, and `get_socket_dest`, which simply retrieves the socket path as a string. The module supports both Unix and TCP/UDP socket formats, adapting to different configurations. It also handles IPv4 and IPv6 addresses, extracting the necessary details from the provided socket path.'
ai_when_to_use: Use this module when you need to obtain the Docker socket path in OpenWrt applications, particularly when working with Docker configurations that may vary in format.
ai_related_topics:
- get_socket_dest_compat
- get_socket_dest
---
# docker_socket.uc
```ucode

// Copyright 2025 Paul Donald / luci-lib-docker-js
// Licensed to the public under the Apache License 2.0.
// Built against the docker v1.47 API

import { cursor } from 'uci';
import * as socket from 'socket';

/**
 * Get the Docker socket path from uci config, more backwards compatible.
 */
export function get_socket_dest_compat() {
	const ctx = cursor();
	let sock_entry = ctx.get_first('dockerd', 'globals', 'hosts')?.[0] || '/var/run/docker.sock';
	ctx.unload();

	sock_entry = lc(sock_entry);
	/* start ucode 2025-12-01 compatibility */
	let sock_split, addr = sock_entry, proto, proto_num, port = 0;
	let family;

	if (index(sock_entry, '://') != -1) {
		let sock_split = split(lc(sock_entry), '://', 2);
		addr = sock_split?.[1];
		proto = sock_split?.[0];
	} 
	if (index(addr, '/') != -1) {
		// we got '/var/run/docker.sock' format
		return socket.sockaddr(addr);
	}

	if (proto === 'tcp' || proto === 'udp' || proto === 'inet') {
		family = socket.AF_INET;
		if (proto === 'tcp')
			proto_num = socket.IPPROTO_TCP;
		else if (proto === 'udp')
			proto_num =  socket.IPPROTO_UDP;
	}
	else if (proto === 'tcp6' || proto === 'udp6' || proto === 'inet6') {
		family = socket.AF_INET6;
		if (proto === 'tcp6')
			proto_num = socket.IPPROTO_TCP;
		else if (proto === 'udp6')
			proto_num =  socket.IPPROTO_UDP;
	}
	else if (proto === 'unix')
		family = socket.AF_UNIX;
	else {
		family = socket.AF_INET; // ipv4
		proto_num = socket.IPPROTO_TCP; // tcp
	}

	let host = addr;
	const l_bracket = index(host, '[');
	const r_bracket = rindex(host, ']');
	if (l_bracket != -1 && r_bracket != -1) {
		host = substr(host, l_bracket + 1, r_bracket - 1);
		family = socket.AF_INET6;
	}

	// find port based on addr, otherwise we find ':' in IPv6
	const port_index = rindex(addr, ':');
	if (port_index != -1) {
		port = int(substr(addr, port_index + 1)) || 0;
		host = substr(host, 0, port_index);
	}

	const sock = socket.addrinfo(host, port, {protocol: proto_num});

	return socket.sockaddr(sock[0].addr);
	// return {family: family, address: host, port: port};
};


/**
 * Get the Docker socket path from uci config
 */
export function get_socket_dest() {

	const ctx = cursor();
	let sock_entry = ctx.get_first('dockerd', 'globals', 'hosts')?.[0] || '/var/run/docker.sock';
	sock_entry = lc(sock_entry);
	let sock_addr = split(sock_entry, '://', 2)?.[1] ?? sock_entry;
	ctx.unload();

	return sock_addr;
};

```
