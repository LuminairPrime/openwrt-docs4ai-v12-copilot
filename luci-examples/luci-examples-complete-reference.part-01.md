---
module: luci-examples
total_token_count: 99980
section_count: 26
is_monolithic: false
is_sharded_part: true
part_number: 1
part_count: 2
generated: '2026-03-28T12:00:00.596003+00:00'
---

# luci-examples Complete Reference (Part 1 of 2)

> **Contains:** 26 documents
> **Tokens:** ~99980 (cl100k_base)
> **Index:** [./luci-examples-complete-reference.md](./luci-examples-complete-reference.md)

---

# commands.js
```javascript
'use strict';

'require view';
'require form';

return view.extend({
	render: function(data) {
		let m, s, o;

		m = new form.Map('luci', _('Custom Commands'),
			_('This page allows you to configure custom shell commands which can be easily invoked from the web interface.'));

		s = m.section(form.GridSection, 'command');
		s.nodescriptions = true;
		s.anonymous = true;
		s.addremove = true;

		o = s.option(form.Value, 'name', _('Description'),
			_('A short textual description of the configured command'));

		o = s.option(form.Value, 'command', _('Command'), _('Command line to execute'));
		o.textvalue = function(section_id) {
			return E('code', [ this.cfgvalue(section_id) ]);
		};

		o = s.option(form.Flag, 'param', _('Custom arguments'),
			_('Allow the user to provide additional command line arguments'));

		o = s.option(form.Flag, 'public', _('Public access'),
			_('Allow executing the command and downloading its output without prior authentication'));

		return m.render();
	}
});

```

---

# commands.uc
```ucode
// Copyright 2012-2022 Jo-Philipp Wich <jow@openwrt.org>
// Licensed to the public under the Apache License 2.0.

'use strict';

import { basename, mkstemp, popen } from 'fs';
import { urldecode } from 'luci.http';

// Decode a given string into arguments following shell quoting rules
// [[abc\ def "foo\"bar" abc'def']] -> [[abc def]] [[foo"bar]] [[abcdef]]
function parse_args(str) {
	let args = [];

	function isspace(c) {
		if (c == 9 || c == 10 || c == 11 || c == 12 || c == 13 || c == 32)
			return c;
	}

	function isquote(c) {
		if (c == 34 || c == 39 || c == 96)
			return c;
	}

	function isescape(c) {
		if (c == 92)
			return c;
	}

	function ismeta(c) {
		if (c == 36 || c == 92 || c == 96)
			return c;
	}

	// Scan substring defined by the indexes [s, e] of the string "str",
	// perform unquoting and de-escaping on the fly and store the result
	function unquote(start, end) {
		let esc, quote, res = [];

		for (let off = start; off < end; off++) {
			const byte = ord(str, off);
			const q = isquote(byte);
			const e = isescape(byte);
			const m = ismeta(byte);

			if (esc) {
				if (!m)
					push(res, 92);

				push(res, byte);
				esc = false;
			}
			else if (e && quote != 39) {
				esc = true;
			}
			else if (q && quote && q == quote) {
				quote = null;
			}
			else if (q && !quote) {
				quote = q;
			}
			else {
				push(res, byte);
			}
		}

		push(args, chr(...res));
	}

	// Find substring boundaries in "str". Ignore escaped or quoted
	// whitespace, pass found start- and end-index for each substring
	// to unquote()
	let esc, start, quote;

	for (let off = 0; off <= length(str); off++) {
		const byte = ord(str, off);
		const q = isquote(byte);
		const s = isspace(byte) ?? (byte === null);
		const e = isescape(byte);

		if (esc) {
			esc = false;
		}
		else if (e && quote != 39) {
			esc = true;
			start ??= off;
		}
		else if (q && quote && q == quote) {
			quote = null;
		}
		else if (q && !quote) {
			start ??= off;
			quote = q;
		}
		else if (s && !quote) {
			if (start !== null) {
				unquote(start, off);
				start = null;
			}
		}
		else {
			start ??= off;
		}
	}

	// If the "quote" is still set we encountered an unfinished string
	if (quote)
		unquote(start, length(str));

	return args;
}

function test_binary(str) {
	for (let off = 0, byte = ord(str); off < length(str); byte = ord(str, ++off))
		if (byte <= 8 || (byte >= 14 && byte <= 31))
			return true;

	return false;
}

function parse_cmdline(cmdid, args) {
	if (uci.get('luci', cmdid) == 'command') {
		let cmd = uci.get_all('luci', cmdid);
		let argv = parse_args(cmd?.command);

		if (cmd?.param == '1') {
			if (length(args))
				push(argv, ...(parse_args(urldecode(args)) ?? []));
			else if (length(args = http.formvalue('args')))
				push(argv, ...(parse_args(args) ?? []));
		}

		return map(argv, v => match(v, /[^\w.\/|-]/) ? `'${replace(v, "'", "'\\''")}'` : v);
	}
}

function execute_command(callback, ...args) {
	let argv = parse_cmdline(...args);

	if (argv) {
		let outfd = mkstemp();
		let errfd = mkstemp();

		const exitcode = system(`${join(' ', argv)} >&${outfd.fileno()} 2>&${errfd.fileno()}`);

		outfd.seek(0);
		errfd.seek(0);

		const stdout = outfd.read(1024 * 512) ?? '';
		const stderr = errfd.read(1024 * 512) ?? '';

		outfd.close();
		errfd.close();

		const binary = test_binary(stdout);

		callback({
			ok:      true,
			command: join(' ', argv),
			stdout:  binary ? null : stdout,
			stderr,
			exitcode,
			binary
		});
	}
	else {
		callback({
			ok:     false,
			code:   404,
			reason: "No such command"
		});
	}
}

function return_json(result) {
	if (result.ok) {
		http.prepare_content('application/json');
		http.write_json(result);
	}
	else {
		http.status(result.code, result.reason);
	}
}


function return_html(result) {
	if (result.ok) {
		include('commands_public', result);
	}
	else {
		http.status(result.code, result.reason);
	}
}

return {
	action_run: function(...args) {
		execute_command(return_json, ...args);
	},

	action_download: function(...args) {
		const argv = parse_cmdline(...args);

		if (argv) {
			const fd = popen(`${join(' ', argv)} 2>/dev/null`);

			if (fd) {
				let filename = replace(basename(argv[0]), /\W+/g, '.');
				let chunk = fd.read(4096) ?? '';
				let name;

				if (test_binary(chunk)) {
					http.header("Content-Disposition", `attachment; filename=${filename}.bin`);
					http.prepare_content("application/octet-stream");
				}
				else {
					http.header("Content-Disposition", `attachment; filename=${filename}.txt`);
					http.prepare_content("text/plain");
				}

				while (length(chunk)) {
					http.write(chunk);
					chunk = fd.read(4096);
				}

				fd.close();
			}
			else {
				http.status(500, "Failed to execute command");
			}
		}
		else {
			http.status(404, "No such command");
		}
	},

	action_public: function(cmdid, ...args) {
		let disp = false;

		if (substr(cmdid, -1) == "s") {
			disp = true;
			cmdid = substr(cmdid, 0, -1);
		}

		if (cmdid &&
		    uci.get('luci', cmdid) == 'command' &&
		    uci.get('luci', cmdid, 'public') == '1')
		{
			if (disp)
				execute_command(return_html, cmdid, ...args);
			else
				this.action_download(cmdid, args);
		}
		else {
			http.status(403, "Access to command denied");
		}
	}
};

```

---

# overview.js
```javascript
'use strict';
'require ui';
'require view';
'require dom';
'require poll';
'require uci';
'require rpc';
'require fs';
'require form';
'require network';
'require tools.widgets as widgets';

return view.extend({

	NextUpdateStrings : {
		'Verify' : _("Verify"),
		'Run once' : _("Run once"),
		'Disabled' : _("Disabled"),
		'Stopped' : _("Stopped")
	},

	time_res : {
		seconds : 1,
		minutes : 60,
		hours : 3600,
	},

	callGetLogServices: rpc.declare({
		object: 'luci.ddns',
		method: 'get_services_log',
		params: [ 'service_name' ],
		expect: {  },
	}),

	callInitAction: rpc.declare({
		object: 'luci',
		method: 'setInitAction',
		params: [ 'name', 'action' ],
		expect: { result: false }
	}),

	callDDnsGetStatus: rpc.declare({
		object: 'luci.ddns',
		method: 'get_ddns_state',
		expect: {  }
	}),

	callDDnsGetEnv: rpc.declare({
		object: 'luci.ddns',
		method: 'get_env',
		expect: {  }
	}),

	callDDnsGetServicesStatus: rpc.declare({
		object: 'luci.ddns',
		method: 'get_services_status',
		expect: {  }
	}),

	services: {},

	status: {},

	/*
	 * Services list is generated by 3 different sources:
	 * 1. /usr/share/ddns/default contains the service installed by package-manager
	 * 2. /usr/share/ddns/custom contains any service installed by the
	 *    user or the ddns script (for example when services are
	 *    downloaded)
	 * 3. /usr/share/ddns/list contains all the services that can be
	 *    downloaded by using the ddns script ('service on demand' feature)
	 *
	 * (Special services that requires a dedicated package ARE NOT
	 * supported by the 'service on demand' feature)
	 */
	callGenServiceList(m, ev) {
		return Promise.all([
			L.resolveDefault(fs.list('/usr/share/ddns/default'), []),
			L.resolveDefault(fs.list('/usr/share/ddns/custom'), []),
			L.resolveDefault(fs.read('/usr/share/ddns/list'), null)
		]).then(L.bind(function ([default_service, custom_service, list_service]) {

			list_service = list_service?.split("\n") || [];
			let _this = this;

			this.services = {};

			default_service.forEach(function (service) {
				_this.services[service.name.replace('.json','')] = true
			});

			custom_service.forEach(function (service) {
				_this.services[service.name.replace('.json','')] = true
			});

			this.services = Object.fromEntries(Object.entries(this.services).sort());

			list_service.forEach(function (service) {
				if (!_this.services[service])
					_this.services[service] = false;
			});
		}, this))
	},

	/*
	* Figure out what the wan interface on the device is.
	* Determine if the physical device exist, or if we should use an alias.
	*/
	callGetWanInterface(m, ev) {
		return network.getDevice('wan').then(dev => dev.getName())
			.catch(err => network.getNetwork('wan').then(net => '@' + net.getName()))
			.catch(err => null);
	},

	/*
	* Check whether or not the service is supported.
	* If the script doesn't find any JSON, assume a 'service on demand' install.
	* If a JSON is found, check if the IP type is supported.
	* Invalidate the service_name if it is not supported.
	*/
	handleCheckService (s, service_name, ipv6, ev, section_id) {

		var value = service_name.formvalue(section_id);
		s.service_supported = null;
		service_name.triggerValidation(section_id);

		return this.handleGetServiceData(value)
			.then(L.bind(function (service_data) {
				if (value != '-' && service_data) {
					service_data = JSON.parse(service_data);
					if (ipv6.formvalue(section_id) == "1" && !service_data.ipv6) {
						s.service_supported = false;
						return;
					}
				}
				s.service_supported = true;
			}, service_name))
			.then(L.bind(service_name.triggerValidation, service_name, section_id))
	},

	handleGetServiceData(service) {
		return Promise.all([
			L.resolveDefault(fs.read('/usr/share/ddns/custom/'+service+'.json'), null),
			L.resolveDefault(fs.read('/usr/share/ddns/default/'+service+'.json'), null)
		]).then(function(data) {
			return data[0] || data[1] || null;
		})
	},

	handleInstallService(m, service_name, section_id, section, _this, ev) {
		var service = service_name.formvalue(section_id)
		return fs.exec('/usr/bin/ddns', ['service', 'install', service])
			.then(L.bind(_this.callGenServiceList, _this))
			.then(L.bind(m.render, m))
			.then(L.bind(this.renderMoreOptionsModal, this, section))
			.catch(function(e) { ui.addNotification(null, E('p', e.message)) });
	},

	handleRefreshServicesList(m, ev) {
		return fs.exec('/usr/bin/ddns', ['service', 'update'])
			.then(L.bind(this.load, this))
			.then(L.bind(this.render, this))
			.catch(function(e) { ui.addNotification(null, E('p', e.message)) });
	},

	handleReloadDDnsRule(m, section_id, ev) {
		return fs.exec('/usr/lib/ddns/dynamic_dns_lucihelper.sh',
							[ '-S', section_id, '--', 'start' ])
			.then(L.bind(m.load, m))
			.then(L.bind(m.render, m))
			.catch(function(e) { ui.addNotification(null, E('p', e.message)) });
	},

	HandleStopDDnsRule(m, section_id, ev) {
		return fs.exec('/usr/lib/ddns/dynamic_dns_lucihelper.sh',
							[ '-S', section_id, '--', 'start' ])
			.then(L.bind(m.render, m))
			.catch(function(e) { ui.addNotification(null, E('p', e.message)) });
	},

	handleToggleDDns(m, ev) {
        let action = this.status['_enabled'];
		return this.callInitAction('ddns', action ? 'disable' : 'enable')
			.then(L.bind(function () { return this.callInitAction('ddns', action ? 'stop' : 'start')}, this))
			.then(L.bind(m.render, m))
			.catch(function(e) { ui.addNotification(null, E('p', e.message)) });
	},

	handleRestartDDns(m, ev) {
		return this.callInitAction('ddns', 'restart')
			.then(L.bind(m.render, m));
	},

	poll_status(map, data) {
		var status = this.status = data[1] || [];
		var service = data[0] || [], rows = map.querySelectorAll('.cbi-section-table-row[data-sid]'),
			ddns_enabled = map.querySelector('[data-name="_enabled"]').querySelector('.cbi-value-field'),
			ddns_toggle = map.querySelector('[data-name="_toggle"]').querySelector('button'),
			services_list = map.querySelector('[data-name="_services_list"]').querySelector('.cbi-value-field');

		ddns_toggle.innerHTML = status['_enabled'] ? _('Stop DDNS') : _('Start DDNS');
		services_list.innerHTML = status['_services_list'];

		dom.content(ddns_enabled, function() {
			return E([], [
				E('div', {}, status['_enabled'] ? _('DDNS Autostart enabled') : [
					_('DDNS Autostart disabled'),
					E('div', { 'class' : 'cbi-value-description' },
					_("Currently DDNS updates are not started at boot or on interface events.") + "<br />" +
					_("This is the default if you run DDNS scripts by yourself (i.e. via cron with force_interval set to '0')"))
				]),]);
		});

		for (var i = 0; i < rows.length; i++) {
			const section_id = rows[i].getAttribute('data-sid');
			const cfg_detail_ip = rows[i].querySelector('[data-name="_cfg_detail_ip"]');
			const cfg_update = rows[i].querySelector('[data-name="_cfg_update"]');
			const cfg_status = rows[i].querySelector('[data-name="_cfg_status"]');
			const reload = rows[i].querySelector('.cbi-section-actions .reload');
			const stop = rows[i].querySelector('.cbi-section-actions .stop');
			const cfg_enabled = uci.get('ddns', section_id, 'enabled');

			reload.disabled = (status['_enabled'] == 0 || cfg_enabled == 0);
			stop.disabled = (!service[section_id].pid);

			const host = uci.get('ddns', section_id, 'lookup_host') || _('Configuration Error');
			const ip = service[section_id]?.ip || _('No Data');
			const last_update = service[section_id]?.last_update || _('Never');
			const next_update = this.NextUpdateStrings[service[section_id]?.next_update] || service[section_id]?.next_update || _('Unknown');
			const next_check = service[section_id]?.next_check || _('Unknown');
			const service_status = service[section_id]?.pid ? '<b>' + _('Running') + '</b> : ' + service[section_id]?.pid : '<b>' + _('Not Running') + '</b>';

			cfg_detail_ip.innerHTML = host + '<br />' + ip;
			cfg_update.innerHTML = last_update + '<br />' + next_check + '<br />' + next_update ;
			cfg_status.innerHTML = service_status;
		}

		return;
	},

	load() {
		return Promise.all([
			this.callDDnsGetServicesStatus(),
			this.callDDnsGetStatus(),
			this.callDDnsGetEnv(),
			this.callGenServiceList(),
			this.callGetWanInterface(),
			uci.load('ddns'),
		]);
	},

	render([resolved, status, env,  , wan_interface]) {
		this.status = status;
		const logdir = uci.get('ddns', 'global', 'ddns_logdir') || "/var/log/ddns";

		let _this = this;

		let m, s, o;

		m = new form.Map('ddns', _('Dynamic DNS'));

		s = m.section(form.NamedSection, 'global', 'ddns',);

		s.tab('info', _('Information'));
		s.tab('global', _('Global Settings'));

		o = s.taboption('info', form.DummyValue, '_version', _('Dynamic DNS Version'));
		o.cfgvalue = function() {
			return status[this.option];
		};

		o = s.taboption('info', form.DummyValue, '_enabled', _('State'));
		o.cfgvalue = function() {
			const res = status[this.option];
			if (!res) {
				this.description = _("Currently DDNS updates are not started at boot or on interface events.") + "<br />" +
				_("This is the default if you run DDNS scripts by yourself (i.e. via cron with force_interval set to '0')")
			}
			return res ? _('DDNS Autostart enabled') : _('DDNS Autostart disabled')
		};

		o = s.taboption('info', form.Button, '_toggle');
		o.title      = '&#160;';
		o.inputtitle = _((status['_enabled'] ? 'Stop' : 'Start') + ' DDNS');
		o.inputstyle = 'apply';
		o.onclick = L.bind(this.handleToggleDDns, this, m);

		o = s.taboption('info', form.Button, '_restart');
		o.title      = '&#160;';
		o.inputtitle = _('Restart DDns');
		o.inputstyle = 'apply';
		o.onclick = L.bind(this.handleRestartDDns, this, m);

		o = s.taboption('info', form.DummyValue, '_services_list', _('Services list last update'));
		o.cfgvalue = function() {
			return status[this.option];
		};

		o = s.taboption('info', form.Button, '_refresh_services');
		o.title      = '&#160;';
		o.inputtitle = _('Update DDns Services List');
		o.inputstyle = 'apply';
		o.onclick = L.bind(this.handleRefreshServicesList, this, m);

		// DDns hints

		if (!env['has_ipv6']) {
			o = s.taboption('info', form.DummyValue, '_no_ipv6');
			o.rawhtml  = true;
			o.title = '<b>' + _("IPv6 not supported") + '</b>';
			o.cfgvalue = function() { return _("IPv6 is not supported by this system") + "<br />" +
			_("Please follow the instructions on OpenWrt's homepage to enable IPv6 support") + "<br />" +
			_("or update your system to the latest OpenWrt Release")};
		}

		if (!env['has_ssl']) {
			o = s.taboption('info', form.DummyValue, '_no_https');
			o.titleref = L.url("admin", "system", "package-manager")
			o.rawhtml  = true;
			o.title = '<b>' + _("HTTPS not supported") + '</b>';
			o.cfgvalue = function() { return _("Neither GNU Wget with SSL nor cURL is installed to support secure updates via HTTPS protocol.") +
			"<br />- " +
			_("You should install 'wget' or 'curl' or 'uclient-fetch' with 'libustream-*ssl' package.") +
			"<br />- " +
			_("In some versions cURL/libcurl in OpenWrt is compiled without proxy support.")};
		}

		if (!env['has_bindnet']) {
			o = s.taboption('info', form.DummyValue, '_no_bind_network');
			o.titleref = L.url("admin", "system", "package-manager")
			o.rawhtml  = true;
			o.title = '<b>' + _("Binding to a specific network not supported") + '</b>';
			o.cfgvalue = function() { return _("Neither GNU Wget with SSL nor cURL is installed to select a network to use for communication.") +
			"<br />- " +
			_("This is only a problem with multiple WAN interfaces and your DDNS provider is unreachable via one of them.") +
			"<br />- " +
			_("You should install 'wget' or 'curl' package.") +
			"<br />- " +
			_("GNU Wget will use the IP of given network, cURL will use the physical interface.") +
			"<br />- " +
			_("In some versions cURL/libcurl in OpenWrt is compiled without proxy support.")};
		}

		if (!env['has_proxy']) {
			o = s.taboption('info', form.DummyValue, '_no_proxy');
			o.titleref = L.url("admin", "system", "package-manager")
			o.rawhtml  = true;
			o.title = '<b>' + _("cURL without Proxy Support") + '</b>';
			o.cfgvalue = function() { return _("cURL is installed, but libcurl was compiled without proxy support.") +
			"<br />- " +
			_("You should install 'wget' or 'uclient-fetch' package or replace libcurl.") +
			"<br />- " +
			_("In some versions cURL/libcurl in OpenWrt is compiled without proxy support.")};
		}

		if (!env['has_bindhost']) {
			o = s.taboption('info', form.DummyValue, '_no_dnstcp');
			o.titleref = L.url("admin", "system", "package-manager")
			o.rawhtml  = true;
			o.title = '<b>' + _("DNS requests via TCP not supported") + '</b>';
			o.cfgvalue = function() { return _("BusyBox's nslookup and hostip do not support TCP " +
				"instead of the default UDP when sending requests to the DNS server!") +
				"<br />- " +
				_("Install 'bind-host' or 'knot-host' or 'drill' package if you know you need TCP for DNS requests.")};
		}

		if (!env['has_dnsserver']) {
			o = s.taboption('info', form.DummyValue, '_no_dnsserver');
			o.titleref = L.url("admin", "system", "package-manager")
			o.rawhtml  = true;
			o.title = '<b>' + _("Using specific DNS Server not supported") + '</b>';
			o.cfgvalue = function() { return _("BusyBox's nslookup in the current compiled version " +
			"does not handle given DNS Servers correctly!") +
			"<br />- " +
			_("You should install 'bind-host' or 'knot-host' or 'drill' or 'hostip' package, " +
			"if you need to specify a DNS server to detect your registered IP.")};
		}

		if (env['has_ssl'] && !env['has_cacerts']) {
			o = s.taboption('info', form.DummyValue, '_no_certs');
			o.titleref = L.url("admin", "system", "package-manager")
			o.rawhtml  = true;
			o.title = '<b>' + _("No certificates found") + '</b>';
			o.cfgvalue = function() { return _("If using secure communication you should verify server certificates!") +
			"<br />- " +
			_("Install 'ca-certificates' package or needed certificates " +
				"by hand into /etc/ssl/certs default directory")};
		}

		// Advanced Configuration Section

		o = s.taboption('global', form.Flag, 'upd_privateip', _("Allow non-public IPs"));
		o.description = _("Non-public and by default blocked IPs") + ':'
		+ '<br /><strong>IPv4: </strong>'
		+ '0/8, 10/8, 100.64/10, 127/8, 169.254/16, 172.16/12, 192.168/16'
		+ '<br /><strong>IPv6: </strong>'
		+ '::/32, f000::/4';
		o.default = "0";
		o.optional = true;

		o = s.taboption('global', form.Value, 'ddns_dateformat', _('Date format'));
		o.description = '<a href="http://www.cplusplus.com/reference/ctime/strftime/" target="_blank">'
			+ _("For supported codes look here")
			+ '</a><br />' +
			_('Current setting: ') + '<b>' + status['_curr_dateformat'] + '</b>';
		o.default = "%F %R"
		o.optional = true;
		o.rmempty = true;

		o = s.taboption('global', form.Value, 'ddns_rundir', _('Status directory'));
		o.description = _('Contains PID and other status information for each running section.');
		o.default = "/var/run/ddns";
		o.optional = true;
		o.rmempty = true;

		o = s.taboption('global', form.Value, 'ddns_logdir', _('Log directory'));
		o.description = _('Contains Log files for each running section.');
		o.default = "/var/log/ddns";
		o.optional = true;
		o.rmempty = true;
		o.validate = function(section_id, formvalue) {
			if (formvalue.indexOf('../') !== -1)
				return _('"../" not allowed in path for Security Reason.')

			return true;
		}

		o = s.taboption('global', form.Value, 'ddns_loglines', _('Log length'));
		o.description = _('Number of last lines stored in log files');
		o.datatype = 'min(1)';
		o.default = '250';

		if (env['has_wget'] && env['has_curl']) {

			o = s.taboption('global', form.Flag, 'use_curl', _('Use cURL'));
			o.description = _('If Wget and cURL package are installed, Wget is used for communication by default.');
			o.default = "0";
			o.optional = true;
			o.rmempty = true;

		}

		o = s.taboption('global', form.Value, 'cacert', _('CA cert bundle file'));
		o.description = _('CA certificate bundle file that will be used to download services data. Set IGNORE to skip certificate validation.');
		o.placeholder = 'IGNORE';
		o.write = function(section_id, value) {
			uci.set('ddns', section_id, 'cacert', value == 'ignore' ? value.toUpperCase() : value);
		};

		o = s.taboption('global', form.Value, 'services_url', _('Services URL Download'));
		o.description = _('Source URL for services file. Defaults to the master openwrt ddns package repo.');
		o.placeholder = 'https://raw.githubusercontent.com/openwrt/packages/master/net/ddns-scripts/files';

		// DDns services
		s = m.section(form.GridSection, 'service', _('Services'));
		s.anonymous = true;
		s.addremove = true;
		s.addbtntitle = _('Add new services...');
		s.sortable  = true;

		s.handleCreateDDnsRule = function(m, name, service_name, ipv6, ev) {
			const section_id = name.isValid('_new_') ? name.formvalue('_new_') : null;
			const service_value = service_name.isValid('_new_') ? service_name.formvalue('_new_') : null;
			const ipv6_value = ipv6.isValid('_new_') ? ipv6.formvalue('_new_') : null;

			if (!section_id || !service_value || !ipv6_value)
				return;

			return m.save(function() {
				uci.add('ddns', 'service', section_id);
				if (service_value != '-') {
					uci.set('ddns', section_id, 'service_name', service_value);
				}
				uci.set('ddns', section_id, 'use_ipv6', ipv6_value);
				ui.hideModal();
			}).then(L.bind(m.children[1].renderMoreOptionsModal, m.children[1], section_id));
		};

		s.handleAdd = function(ev) {
			let m2 = new form.Map('ddns');
			let s2 = m2.section(form.NamedSection, '_new_');
			let name, ipv6, service_name;

			s2.render = function() {
				return Promise.all([
					{},
					this.renderUCISection('_new_')
				]).then(this.renderContents.bind(this));
			};

			name = s2.option(form.Value, 'name', _('Name'));
			name.rmempty = false;
			name.datatype = 'uciname';
			name.placeholder = _('New DDns Service…');
			name.validate = function(section_id, value) {
				if (uci.get('ddns', value) != null)
					return _('The service name is already used');

				return true;
			};

			ipv6 = s2.option( form.ListValue, 'use_ipv6',
				_("IP address version"),
				_("Which record type to update at the DDNS provider (A/AAAA)"));
			ipv6.default = '0';
			ipv6.value("0", _("IPv4-Address"))
			if (env["has_ipv6"]) {
				ipv6.value("1", _("IPv6-Address"))
			}

			service_name = s2.option(form.ListValue, 'service_name',
					String.format('%s', _("DDNS Service provider")));
			service_name.value('-',"📝 " + _("custom") );
			Object.keys(_this.services).sort().forEach(name => service_name.value(name));
			service_name.validate = function(section_id, value) {
				if (value == '-') return true;
				if (!value) return _("Select a service");
				if (!s2.service_supported) return _("Service doesn't support this IP type");
				return true;
			};

			ipv6.onchange = L.bind(_this.handleCheckService, _this, s2, service_name, ipv6);
			service_name.onchange = L.bind(_this.handleCheckService, _this, s2, service_name, ipv6);

			m2.render().then(L.bind(function(nodes) {
				ui.showModal(_('Add new services...'), [
					nodes,
					E('div', { 'class': 'right' }, [
						E('button', {
							'class': 'btn',
							'click': ui.hideModal
						}, _('Cancel')), ' ',
						E('button', {
							'class': 'cbi-button cbi-button-positive important',
							'click': ui.createHandlerFn(this, 'handleCreateDDnsRule', m, name, service_name, ipv6)
						}, _('Create service'))
					])
				], 'cbi-modal');

				nodes.querySelector('[id="%s"] input[type="text"]'.format(name.cbid('_new_'))).focus();
			}, this));
		};

		s.renderRowActions = function(section_id) {
			const tdEl = this.super('renderRowActions', [ section_id, _('Edit') ]),
				cfg_enabled = uci.get('ddns', section_id, 'enabled'),
				reload_opt = {
					'class': 'cbi-button cbi-button-neutral reload',
					'click': ui.createHandlerFn(_this, 'handleReloadDDnsRule', m, section_id),
					'title': _('Reload this service'),
				},
				stop_opt = {
					'class': 'cbi-button cbi-button-neutral stop',
					'click': ui.createHandlerFn(_this, 'HandleStopDDnsRule', m, section_id),
					'title': _('Stop this service'),
				};

			if (status['_enabled'] == 0 || cfg_enabled == 0)
				reload_opt['disabled'] = 'disabled';

			if (!resolved[section_id] || !resolved[section_id].pid ||
					(resolved[section_id].pid && cfg_enabled == '1'))
				stop_opt['disabled'] = 'disabled';

			dom.content(tdEl.lastChild, [
				E('button', stop_opt, _('Stop')),
				E('button', reload_opt, _('Reload')),
				tdEl.lastChild.childNodes[0],
				tdEl.lastChild.childNodes[1],
				tdEl.lastChild.childNodes[2]
			]);

			return tdEl;
		};

		s.modaltitle = function(section_id) {
			return _('DDns Service') + ' » ' + section_id;
		};

		s.addModalOptions = function(s, section_id) {

			const service = uci.get('ddns', section_id, 'service_name') || '-';
			const ipv6 = uci.get('ddns', section_id, 'use_ipv6');
			let service_name, use_ipv6;

			return _this.handleGetServiceData(service).then(L.bind(function (service_data) {
				s.service_available = true;
				s.service_supported = true;
				s.url = null;

				if (service != '-') {
					if (!service_data)
						s.service_available = false;
					else {
						service_data = JSON.parse(service_data);
						if (ipv6 == "1" && !service_data.ipv6)
							s.service_supported = false;
						else if (ipv6 == "1") {
							s.url = service_data.ipv6.url;
						} else {
							s.url = service_data.ipv4.url;
						}
					}
				}

				s.tab('basic', _('Basic Settings'));
				s.tab('advanced', _('Advanced Settings'));
				s.tab('timer', _('Timer Settings'));
				s.tab('logview', _('Log File Viewer'));

				o = s.taboption('basic', form.Flag, 'enabled',
					_('Enabled'),
					_("If this service section is disabled it will not be started.")
					+ "<br />" +
					_("Neither from LuCI interface nor from console."));
				o.modalonly = true;
				o.rmempty  = false;
				o.default = '1';

				o = s.taboption('basic', form.Value, 'lookup_host',
					_("Lookup Hostname"),
					_("Hostname/FQDN to validate, whether an IP update is necessary"));
				o.rmempty = false;
				o.placeholder = "myhost.example.com";
				o.datatype = 'and(minlength(3),hostname("strict"))';
				o.modalonly = true;

				use_ipv6 = s.taboption('basic', form.ListValue, 'use_ipv6',
					_("IP address version"),
					_("Which record type to update at the DDNS provider (A/AAAA)"));
				use_ipv6.default = '0';
				use_ipv6.modalonly = true;
				use_ipv6.rmempty  = false;
				use_ipv6.value("0", _("IPv4-Address"))
				if (env["has_ipv6"]) {
					use_ipv6.value("1", _("IPv6-Address"))
				}

				service_name = s.taboption('basic', form.ListValue, 'service_name',
					String.format('%s', _("DDNS Service provider")));
				service_name.modalonly = true;
				service_name.value('-',"📝 " + _("custom") );
				Object.keys(_this.services).sort().forEach(name => service_name.value(name));
				service_name.cfgvalue = function(section_id) {
					return uci.get('ddns', section_id, 'service_name') || '-';
				};
				service_name.write = function(section_id, service) {
					if (service != '-') {
						uci.unset('ddns', section_id, 'update_url');
						uci.unset('ddns', section_id, 'update_script');
						return uci.set('ddns', section_id, 'service_name', service);
					}
					return uci.unset('ddns', section_id, 'service_name');
				};
				service_name.validate = function(section_id, value) {
					if (value == '-') return true;
					if (!value) return _("Select a service");
					if (!s.service_available) return _('Service not installed');
					if (!s.service_supported) return _("Service doesn't support this IP type");
					return true;
				};

				service_name.onchange = L.bind(_this.handleCheckService, _this, s, service_name, use_ipv6);
				use_ipv6.onchange = L.bind(_this.handleCheckService, _this, s, service_name, use_ipv6);

				if (!s.service_available) {
					o = s.taboption('basic', form.Button, '_download_service');
					o.modalonly  = true;
					o.title      = _('Service not installed');
					o.inputtitle = _('Install Service');
					o.inputstyle = 'apply';
					o.onclick = L.bind(_this.handleInstallService,
						this, m, service_name, section_id, s.section, _this)
				}

				if (!s.service_supported) {
					o = s.taboption('basic', form.DummyValue, '_not_supported', '&nbsp');
					o.cfgvalue = function () {
						return _("Service doesn't support this IP type")
					};
				}

				if (s.url) {
					o = s.taboption('basic', form.DummyValue, '_url', _("Update URL"));
					o.rawhtml = true;
					o.default = '<div style="font-family: monospace;">'
						+ s.url.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
						+ '</div>';
				}

				let service_switch = s.taboption('basic', form.Button, '_switch_proto');
				service_switch.modalonly  = true;
				service_switch.title      = _('Really switch service?');
				service_switch.inputtitle = _('Switch service');
				service_switch.inputstyle = 'apply';
				service_switch.onclick = L.bind(function(ev) {
					if (!s.service_supported) return;

					return s.map.save()
						.then(L.bind(m.load, m))
						.then(L.bind(m.render, m))
						.then(L.bind(this.renderMoreOptionsModal, this, s.section));
				}, this);

				if (s.service_available && s.service_supported) {

					o = s.taboption('basic', form.Value, 'update_url',
						_("Custom update-URL"),
						_("Update URL for updating your DDNS Provider.")
						+ "<br />" +
						_("Follow instructions found on their WEB page."));
					o.modalonly = true;
					o.rmempty = true;
					o.optional = true;
					o.depends("service_name","-");
					o.validate = function(section_id, value) {
						const other = this.section.formvalue(section_id, 'update_script');
						if ((!value && !other) || (value && other)) {
							return _("Provide either an Update Script OR an Update URL");
						}

						return true;
					};

					o = s.taboption('basic', form.FileUpload, 'update_script',
						_("Custom update-script"),
						_("Custom update script for updating your DDNS Provider."));
					o.root_directory = '/usr/lib/ddns/';
					o.datatype = 'file';
					o.show_hidden = true;
					o.enable_upload = true;
					o.enable_remove = true;
					o.enable_download = true;
					o.modalonly = true;
					o.rmempty = true;
					o.optional = true;
					o.depends("service_name","-");
					o.validate = function(section_id, value) {
						const other = this.section.formvalue(section_id, 'update_url');
						if ((!value && !other) || (value && other)) {
							return _("Provide either an Update Script OR an Update URL");
						}

						return true;
					};

					o = s.taboption('basic', form.Value, 'domain',
						_("Domain"),
						_("Replaces [DOMAIN] in Update-URL (URL-encoded)"));
					o.modalonly = true;
					o.rmempty = false;

					o = s.taboption('basic', form.Value, 'username',
						_("Username"),
						_("Replaces [USERNAME] in Update-URL (URL-encoded)"));
					o.modalonly = true;
					o.rmempty = false;

					o = s.taboption('basic', form.Value, 'password',
						_("Password"),
						_("Replaces [PASSWORD] in Update-URL (URL-encoded)")
						+ '<br/>' +
						_("A.k.a. the TOKEN at e.g. afraid.org"));
					o.password = true;
					o.modalonly = true;
					o.rmempty = false;

					o = s.taboption('basic', form.Value, 'param_enc',
						_("Optional Encoded Parameter"),
						_("Optional: Replaces [PARAMENC] in Update-URL (URL-encoded)"));
					o.optional = true;
					o.modalonly = true;

					o = s.taboption('basic', form.Value, 'param_opt',
						_("Optional Parameter"),
						_("Optional: Replaces [PARAMOPT] in Update-URL (NOT URL-encoded)"));
					o.optional = true;
					o.modalonly = true;

					if (env['has_ssl']) {
						o = s.taboption('basic', form.Flag, 'use_https',
							_("Use HTTP Secure"),
							_("Enable secure communication with DDNS provider"));
						o.optional = true;
						o.modalonly = true;

						o = s.taboption('basic', form.Value, 'cacert',
							_("Path to CA-Certificate"),
							_("directory or path/file")
							+ "<br />" +
							_("or")
							+ '<b>' + " IGNORE " + '</b>' +
							_("to run HTTPS without verification of server certificates (insecure)"));
						o.modalonly = true;
						o.depends("use_https", "1");
						o.placeholder = "/etc/ssl/certs";
						o.rmempty = false;
						o.optional = true;
						o.write = function(section_id, value) {
							uci.set('ddns', section_id, 'cacert', value == 'ignore' ? value.toUpperCase() : value);
						};
					};


					o = s.taboption('advanced', form.ListValue, 'ip_source',
						_("IP address source"),
						_("Method used to determine the system IP-Address to send in updates"));
					o.modalonly = true;
					o.default = "network";
					o.value("network", _("Network"));
					o.value("web", _("URL"));
					o.value("interface", _("Interface"));
					o.value("script", _("Script"));
					o.write = function(section_id, formvalue) {
						switch(formvalue) {
							case 'network':
								uci.unset('ddns', section_id, "ip_url");
								uci.unset('ddns', section_id, "ip_interface");
								uci.unset('ddns', section_id, "ip_script");
								break;
							case 'web':
								uci.unset('ddns', section_id, "ip_network");
								uci.unset('ddns', section_id, "ip_interface");
								uci.unset('ddns', section_id, "ip_script");
								break;
							case 'interface':
								uci.unset('ddns', section_id, "ip_network");
								uci.unset('ddns', section_id, "ip_url");
								uci.unset('ddns', section_id, "ip_script");
								break;
							case 'script':
								uci.unset('ddns', section_id, "ip_network");
								uci.unset('ddns', section_id, "ip_url");
								uci.unset('ddns', section_id, "ip_interface");
								break;
							default:
								break;
						};

						return uci.set('ddns', section_id, 'ip_source', formvalue )
					};

					o = s.taboption('advanced', widgets.NetworkSelect, 'ip_network',
						_("Network"),
						_("Defines the network to read systems IP-Address from"));
					o.depends('ip_source','network');
					o.modalonly = true;
					o.default = 'wan';
					o.multiple = false;

					o = s.taboption('advanced', form.Value, 'ip_url',
						_("URL to detect"),
						_("Defines the Web page to read systems IP-Address from.")
						+ '<br />' +
						String.format('%s %s', _('Example for IPv4'), ': http://checkip.dyndns.com')
						+ '<br />' +
						String.format('%s %s', _('Example for IPv6'), ': http://checkipv6.dyndns.com'));
					o.depends("ip_source", "web")
					o.modalonly = true;

					o = s.taboption('advanced', widgets.DeviceSelect, 'ip_interface',
						_("Interface"),
						_("Defines the interface to read systems IP-Address from"));
					o.modalonly = true;
					o.depends("ip_source", "interface")
					o.multiple = false;
					o.default = wan_interface;

					o = s.taboption('advanced', form.Value, 'ip_script',
						_("Script"),
						_("User defined script to read system IP-Address"));
					o.modalonly = true;
					o.depends("ip_source", "script")
					o.placeholder = "/path/to/script.sh"

					o = s.taboption('advanced', widgets.NetworkSelect, 'interface',
						_("Event Network"),
						_("Network on which the ddns-updater scripts will be started"));
					o.modalonly = true;
					o.multiple = false;
					o.default = 'wan';
					o.depends("ip_source", "web");
					o.depends("ip_source", "script");
					o.depends("ip_source", "interface");

					o = s.taboption('advanced', form.DummyValue, '_interface',
						_("Event Network"),
						_("Network on which the ddns-updater scripts will be started"));
					o.depends("ip_source", "network");
					o.forcewrite = true;
					o.modalonly = true;
					o.cfgvalue = function(section_id) {
						return uci.get('ddns', section_id, 'interface') || _('This will be autoset to the selected interface');
					};
					o.write = function(section_id) {
						const opt = this.section.formvalue(section_id, 'ip_source');
						const val = this.section.formvalue(section_id, 'ip_'+opt);
						return uci.set('ddns', section_id, 'interface', val);
					};

					if (env['has_bindnet']) {
						o = s.taboption('advanced', widgets.NetworkSelect, 'bind_network',
							_("Bind Network"),
							_('OPTIONAL: Network to use for communication')
							+ '<br />' +
							_("Network on which the ddns-updater scripts will be started"));
						o.depends("ip_source", "web");
						o.optional = true;
						o.rmempty = true;
						o.modalonly = true;
					}

					if (env['has_forceip']) {
						o = s.taboption('advanced', form.Flag, 'force_ipversion',
							_("Force IP Version"),
							_('OPTIONAL: Force the usage of pure IPv4/IPv6 only communication.'));
						o.optional = true;
						o.rmempty = true;
						o.modalonly = true;
					}

					if (env['has_dnsserver']) {
						o = s.taboption("advanced", form.Value, "dns_server",
							_("DNS-Server"),
							_("OPTIONAL: Use non-default DNS-Server to detect 'Registered IP'.")
							+ "<br />" +
							_("Format: IP or FQDN"));
						o.placeholder = "mydns.lan"
						o.optional = true;
						o.rmempty = true;
						o.modalonly = true;
					}

					if (env['has_bindhost']) {
						o = s.taboption("advanced", form.Flag, "force_dnstcp",
							_("Force TCP on DNS"),
							_("OPTIONAL: Force the use of TCP instead of default UDP on DNS requests."));
						o.optional = true;
						o.rmempty = true;
						o.modalonly = true;
					}

					if (env['has_proxy']) {
						o = s.taboption("advanced", form.Value, "proxy",
							_("PROXY-Server"),
							_("OPTIONAL: Proxy-Server for detection and updates.")
							+ "<br />" +
							String.format('%s: <b>%s</b>', _("Format"), "[user:password@]proxyhost:port")
							+ "<br />" +
							String.format('%s: <b>%s</b>', _("IPv6 address must be given in square brackets"), "[2001:db8::1]:8080"));
						o.optional = true;
						o.rmempty = true;
						o.modalonly = true;
					}

					o = s.taboption("advanced", form.ListValue, "use_syslog",
						_("Log to syslog"),
						_("Writes log messages to syslog. Critical Errors will always be written to syslog."));
					o.modalonly = true;
					o.default = "2"
					o.optional = true;
					o.value("0", _("No logging"))
					o.value("1", _("Info"))
					o.value("2", _("Notice"))
					o.value("3", _("Warning"))
					o.value("4", _("Error"))

					o = s.taboption("advanced", form.Flag, "use_logfile",
						_("Log to file"));
					o.default = '1';
					o.optional = true;
					o.modalonly = true;
					o.cfgvalue = function(section_id) {
						this.description = _("Writes detailed messages to log file. File will be truncated automatically.") + "<br />" +
						_("File") + ': "' + logdir + '/' + section_id + '.log"';
						return uci.get('ddns', section_id, 'use_logfile');
					};


					o = s.taboption("timer", form.Value, "check_interval",
						_("Check Interval"));
					o.placeholder = "10";
					o.modalonly = true;
					o.datatype = 'uinteger';
					o.validate = function(section_id, formvalue) {
						const unit = this.section.formvalue(section_id, 'check_unit');
						const time_to_sec = _this.time_res[unit || 'minutes'] * formvalue;

						if (formvalue && time_to_sec < 300)
							return _('Values below 5 minutes == 300 seconds are not supported');

						return true;
					};

					o = s.taboption("timer", form.ListValue, "check_unit",
						_('Check Unit'),
						_("Interval unit to check for changed IP"));
					o.modalonly = true;
					o.optional = true;
					o.value("seconds", _("seconds"));
					o.value("minutes", _("minutes"));
					o.value("hours", _("hours"));

					o = s.taboption("timer", form.Value, "force_interval",
						_("Force Interval"),
						_("Interval to force an update at the DDNS Provider")
						+ "<br />" +
						_("Setting this parameter to 0 will force the script to only run once"));
					o.placeholder = "72";
					o.optional = true;
					o.modalonly = true;
					o.datatype = 'uinteger';
					o.validate = function(section_id, formvalue) {

						if (!formvalue)
							return true;

						const check_unit = this.section.formvalue(section_id, 'check_unit');
						const check_val = this.section.formvalue(section_id, 'check_interval');
						const force_unit = this.section.formvalue(section_id, 'force_unit');
						const check_to_sec = _this.time_res[check_unit || 'minutes'] * ( check_val || '30');
						const force_to_sec = _this.time_res[force_unit || 'minutes'] * formvalue;

						if (force_to_sec != 0 && force_to_sec < check_to_sec)
							return _("Values lower than 'Check Interval' except '0' are invalid");

						return true;
					};

					o = s.taboption("timer", form.ListValue, "force_unit",
						_('Force Unit'),
						_("Interval unit for forced updates sent to DDNS Provider."));
					o.modalonly = true;
					o.optional = true;
					o.value("minutes", _("minutes"));
					o.value("hours", _("hours"));
					o.value("days", _("days"));

					o = s.taboption("timer", form.Value, "retry_max_count",
						_("Error Max Retry Counter"),
						_("On Error the script will stop execution after the given number of retries.")
						+ "<br />" +
						_("The default setting of '0' will retry infinitely."));
					o.placeholder = "0";
					o.optional = true;
					o.modalonly = true;
					o.datatype = 'uinteger';

					o = s.taboption("timer", form.Value, "retry_interval",
						_("Error Retry Interval"),
  						_("The interval between which each subsequent retry commences."));
					o.placeholder = "60";
					o.optional = true;
					o.modalonly = true;
					o.datatype = 'uinteger';

					o = s.taboption("timer", form.ListValue, "retry_unit",
						_('Retry Unit'),
						_("Which time units to use for retry counters."));
					o.modalonly = true;
					o.optional = true;
					o.value("seconds", _("seconds"));
					o.value("minutes", _("minutes"));

					o = s.taboption('logview', form.Button, '_read_log');
					o.title      = '';
					o.depends('use_logfile','1');
					o.modalonly = true;
					o.inputtitle = _('Read / Reread log file');
					o.inputstyle = 'apply';
					o.onclick = L.bind(function(ev, section_id) {
						return _this.callGetLogServices(section_id).then(L.bind(log_box.update_log, log_box));
					}, this);

					const log_box = s.taboption("logview", form.DummyValue, "_logview");
					log_box.depends('use_logfile','1');
					log_box.modalonly = true;

					log_box.update_log = L.bind(function(view, log_data) {
						return document.getElementById('syslog').textContent = log_data.result;
					}, o, this);

					log_box.render = L.bind(function() {
						return E([
							E('p', {}, _('This is the current content of the log file in %h for this service.').format(logdir)),
							E('p', {}, E('textarea', { 'style': 'width:100%; font-size: 10px', 'rows': 20, 'readonly' : 'readonly', 'id' : 'syslog' }, _('Please press [Read] button') ))
						]);
					}, o, this);
				}

				for (let o of s.children) {
					switch (o.option) {
					case '_switch_proto':
						o.depends({ service_name : service, use_ipv6: ipv6, "!reverse": true })
						continue;
					case 'enabled':
					case 'service_name':
					case 'use_ipv6':
					case 'update_script':
					case 'update_url':
					case 'lookup_host':
						continue;

					default:
						if (o.deps.length)
							for (let d of o.deps) {
								d.service_name = service;
								d.use_ipv6 = ipv6;
							}
						else
							o.depends({service_name: service, use_ipv6: ipv6 });
					}
				}
			}, this)
		)};

		o = s.option(form.DummyValue, '_cfg_status', _('Status'));
		o.modalonly = false;
		o.textvalue = section_id => resolved[section_id]?.pid 
			? `<b>${_('Running')}</b> : ${resolved[section_id].pid}` 
			: `<b>${_('Not Running')}</b>`;


		o = s.option(form.DummyValue, '_cfg_name', _('Name'));
		o.modalonly = false;
		o.textvalue = function(section_id) {
			return '<b>' + section_id + '</b>';
		};

		o = s.option(form.DummyValue, '_cfg_detail_ip', _('Lookup Hostname') + "<br />" + _('Registered IP'));
		o.rawhtml   = true;
		o.modalonly = false;
		o.textvalue = function(section_id) {
			const host = uci.get('ddns', section_id, 'lookup_host') || _('Configuration Error');
			const ip = resolved[section_id]?.ip || _('No Data');

			return host + '<br />' + ip;
		};

		o = s.option(form.Flag, 'enabled', _('Enabled'));
		o.rmempty  = false;
		o.editable = true;
		o.modalonly = false;

		o = s.option(form.DummyValue, '_cfg_update', _('Last Update') + " |<br />" + _('Next Verify') + " |<br />" + _('Next Update'));
		o.rawhtml   = true;
		o.modalonly = false;
		o.textvalue = function(section_id) {
			const last_update = resolved[section_id]?.last_update || _('Never');
			const next_check = resolved[section_id]?.next_check || _('Unknown');
			const next_update = _this.NextUpdateStrings[resolved[section_id]?.next_update] || resolved[section_id]?.next_update || _('Unknown');
			return  last_update + '<br />' + next_check + '<br />' + next_update;
		};

		return m.render().then(L.bind(function(m, nodes) {
			poll.add(L.bind(function() {
				return Promise.all([
					this.callDDnsGetServicesStatus(),
					this.callDDnsGetStatus()
				]).then(L.bind(this.poll_status, this, nodes));
			}, this), 5);
			return nodes;
		}, this, m));
	}
});

```

---

# 70_ddns.js
```javascript
'use strict';
'require baseclass';
'require rpc';
'require uci';

return baseclass.extend({
	title: _('Dynamic DNS'),

	callDDnsGetServicesStatus: rpc.declare({
		object: 'luci.ddns',
		method: 'get_services_status',
		expect: {  }
	}),

	load: function() {
		return Promise.all([
			this.callDDnsGetServicesStatus(),
			uci.load('ddns')
		]);
	},

	render: function(data) {
		var services = data[0];

		var table = E('table', { 'class': 'table' }, [
			E('tr', { 'class': 'tr table-titles' }, [
				E('th', { 'class': 'th' }, _('Configuration')),
				E('th', { 'class': 'th' }, _('Next Update')),
				E('th', { 'class': 'th' }, _('Lookup Hostname')),
				E('th', { 'class': 'th' }, _('Registered IP')),
				E('th', { 'class': 'th' }, _('Network'))
			])
		]);

		cbi_update_table(table, Object.keys(services).map(function(key, index) {
			return [
				key,
				services[key].next_update ? _(services[key].next_update) : _('Unknown'),
				uci.get('ddns',key,'lookup_host'),
				services[key].ip ? services[key].ip : _('No Data'),
				(uci.get('ddns',key,'use_ipv6') == '1' ? 'IPv6' : 'IPv4') + ' / ' + uci.get('ddns',key,'interface')
			];
		}), E('em', _('There is no service configured.')));

		return E([table]);
	}
});

```

---

# ddns.uc
```ucode
#!/usr/bin/env ucode

'use strict';

import { readfile, popen, stat, glob } from 'fs';
import { init_enabled } from 'luci.sys';
import { isnan } from 'math';
import { cursor } from 'uci';

const uci = cursor();
const ddns_log_path = '/var/log/ddns';
const ddns_package_path = '/usr/share/ddns';
const ddns_run_path = '/var/run/ddns';
const luci_helper = '/usr/lib/ddns/dynamic_dns_lucihelper.sh';
const ddns_version_file = '/usr/share/ddns/version';




function get_dateformat() {
	return uci.get('ddns', 'global', 'ddns_dateformat') || '%F %R';
}

function uptime() {
	return split(readfile('/proc/uptime'), ' ')?.[0];
}

function killcmd(procid, signal) {
	if (!signal) {
		signal = 0;
	}
	// by default, we simply re-nice a process to check it is running
	return system(`kill -${signal} ${procid}`);
}

function trimnonewline(input) {
	return replace(trim(input), /\n/g, '');
}

function get_date(seconds, format) {
	return trimnonewline( popen(`date -d @${seconds} "+${format}" 2>/dev/null`, 'r')?.read?.('line') );
}

// convert epoch date to given format
function epoch2date(epoch, format) {
	if (!format || length(format) < 2) {
		format = get_dateformat();
	}
	format = replace(format, /%n/g, '<br />'); // Replace '%n' with '<br />'
	format = replace(format, /%t/g, '    ');   // Replace '%t' with four spaces

	return get_date(epoch, format);
}

// function to calculate seconds from given interval and unit
function calc_seconds(interval, unit) {
	let parsedInterval = int(interval);
	if (isnan(parsedInterval)) {
		return null;
	}

	switch (unit) {
		case 'days':
			return parsedInterval * 86400;  // 60 sec * 60 min * 24 h
		case 'hours':
			return parsedInterval * 3600;   // 60 sec * 60 min
		case 'minutes':
			return parsedInterval * 60;     // 60 sec
		case 'seconds':
			return parsedInterval;
		default:
			return null;
	}
}

const methods = {
	get_services_log: {
		args: { service_name: 'service_name' },
		call: function(request) {
			let result = 'File not found or empty';
			
			// Get the log directory. Fall back to '/var/log/ddns' if not found
			let logdir = uci.get('ddns', 'global', 'ddns_logdir') || ddns_log_path;

			// Fall back to default logdir with insecure path
			if (match(logdir, /\.\.\//)) {
				logdir = ddns_log_path;
			}

			// Check if service_name is provided and log file exists
			if (request.args && request.args.service_name && stat(`${logdir}/${request.args.service_name}.log`)?.type == 'file' ) {
				result = readfile(`${logdir}/${request.args.service_name}.log`);
			}

			uci.unload();
			return { result: result };
		}
	},
	
	get_services_status: {
		call: function() {
			const rundir = uci.get('ddns', 'global', 'ddns_rundir') || ddns_run_path;
			let res = {};

			uci.foreach('ddns', 'service', function(s) {
				/* uci.foreach danger zone: if you inadvertently call uci.unload('ddns')
				anywhere in this foreach loop, you will produce some spectacular undefined behaviour */
				let ip, lastUpdate, nextUpdate, nextCheck;
				const section = s['.name'];
				if (section == '.anonymous')
					return;

				if (stat(`${rundir}/${section}.ip`)?.type == 'file') {
					ip = readfile(`${rundir}/${section}.ip`);
				} else {
					const dnsServer = s['dns_server'] || '';
					const forceIpVersion = int(s['force_ipversion'] || 0);
					const forceDnsTcp = int(s['force_dnstcp'] || 0);
					// const isGlue = int(s['is_glue'] || 0);
					const useIpv6 = int(s['use_ipv6'] || 0);
					const lookupHost = s['lookup_host'] || '_nolookup_';
					let command = [luci_helper];

					if (useIpv6 == 1) push(command, '-6');
					if (forceIpVersion == 1) push(command, '-f');
					if (forceDnsTcp == 1) push(command, '-t');
					// if (isGlue == 1) push(command, '-g');

					push(command, '-l', lookupHost);
					push(command, '-S', section);
					if (length(dnsServer) > 0) push(command, '-d', dnsServer);
					push(command, '-- get_registered_ip');

					const result = system(`${join(' ', command)}`);
				}

				lastUpdate = int(readfile(`${rundir}/${section}.update`) || 0);
				nextCheck = int(readfile(`${rundir}/${section}.nextcheck`) || 0);

				let pid = int(readfile(`${rundir}/${section}.pid`) || 0);

				// if killcmd succeeds (0) to re-nice the process, we do not assume the pid is dead
				if (pid > 0 && killcmd(pid)) {
					pid = 0;
				}

				let _uptime = int(uptime());

				const forcedUpdateInterval = calc_seconds(
					int(s['force_interval']) || 72,
					s['force_unit'] || 'hours'
				);

				const checkInterval = calc_seconds(
					int(s['check_interval']) || 10,
					s['check_unit'] || 'minutes'
				);

				let convertedLastUpdate;
				if (lastUpdate > 0) {
					const epoch = time() - _uptime + lastUpdate;
					convertedLastUpdate = epoch2date(epoch);
					nextUpdate = epoch2date(epoch + forcedUpdateInterval);
				}

				let convertedNextCheck;
				if (nextCheck > 0) {
					const epoch = time() - _uptime + nextCheck;
					convertedNextCheck = epoch2date(epoch);
				}

				if (pid > 0 && (lastUpdate + forcedUpdateInterval - _uptime) <= 0) {
					nextUpdate = 'Verify';
				} else if (forcedUpdateInterval === 0) {
					nextUpdate = 'Run once';
				} else if (pid == 0 && s['enabled'] == '0') {
					nextUpdate = 'Disabled';
				} else if (pid == 0 && s['enabled'] != '0') {
					nextUpdate = 'Stopped';
				}

				res[section] = {
					ip: ip ? replace(trim(ip), '\n', '<br/>') : null,
					last_update: lastUpdate !== 0 ? convertedLastUpdate : null,
					next_update: nextUpdate || null,
					next_check : nextCheck !== 0 ? convertedNextCheck : null,
					pid: pid || null,
				};
			});

			uci.unload('ddns');
			return res;
		}
	},

	get_ddns_state: {
		call: function() {

			const services_mtime = stat(ddns_package_path + '/list')?.mtime;
			let res = {};
			let ver, control;

			if (stat(ddns_version_file)?.type == 'file') {
				ver = readfile(ddns_version_file);
			}

			res['_version'] = ver;
			res['_enabled'] = init_enabled('ddns');
			res['_curr_dateformat'] = epoch2date(time());
			res['_services_list'] = (services_mtime && epoch2date(services_mtime)) || 'NO_LIST';

			uci.unload('ddns');
			return res;
		}
	},

	get_env: {
		call: function () {
			let res = {};
			let cache = {};

			const hasCommand = (command) => { return (system(`command -v ${command} 1>/dev/null`) == 0) ? true : false };

			const hasWget = () => hasCommand('wget');

			const hasWgetSsl = () => {
				if (cache['has_wgetssl']) return cache['has_wgetssl'];
				const result = hasWget() && system(`wget 2>&1 | grep -iqF 'https'`) == 0 ? true : false;
				cache['has_wgetssl'] = result;
				return result;
			};

			const hasGNUWgetSsl = () => {
				if (cache['has_gnuwgetssl']) return cache['has_gnuwgetssl'];
				const result = hasWget() && system(`wget -V 2>&1 | grep -iqF '+https'`) == 0 ? true : false;
				cache['has_gnuwgetssl'] = result;
				return result;
			};

			const hasCurl = () => {
				if (cache['has_curl']) return cache['has_curl'];
				const result = hasCommand('curl');
				cache['has_curl'] = result;
				return result;
			};

			const hasCurlSsl = () => {
				return system(`curl -V 2>&1 | grep -qF 'https'`) == 0 ? true : false;
			};

			const hasFetch = () => {
				if (cache['has_fetch']) return cache['has_fetch'];
				const result = hasCommand('uclient-fetch');
				cache['has_fetch'] = result;
				return result;
			};

			const hasFetchSsl = () => {
				return stat('/lib/libustream-ssl.so') == 0 ? true : false;
			};

			const hasCurlPxy = () => {
				return system(`grep -i 'all_proxy' /usr/lib/libcurl.so*`) == 0 ? true : false;
			};

			const hasBbwget = () => {
				return system(`wget -V 2>&1 | grep -iqF 'busybox'`) == 0 ? true : false;
			};


			res['has_wget'] = hasWget();
			res['has_curl'] = hasCurl();

			res['has_ssl'] = hasGNUWgetSsl() || hasWgetSsl() || hasCurlSsl() || (hasFetch() && hasFetchSsl());
			res['has_proxy'] = hasGNUWgetSsl() || hasWgetSsl() || hasCurlPxy() || hasFetch() || hasBbwget();
			res['has_forceip'] = hasGNUWgetSsl() || hasWgetSsl() || hasCurl() || hasFetch();
			res['has_bindnet'] = hasCurl() || hasGNUWgetSsl();

			const hasBindHost = () => {
				if (cache['has_bindhost']) return cache['has_bindhost'];
				const commands = ['host', 'khost', 'drill'];
				for (let command in commands) {
					if (hasCommand(command)) {
						cache['has_bindhost'] = true;
						return true;
					}
				}

				cache['has_bindhost'] = false;
				return false;
			};

			res['has_bindhost'] = cache['has_bindhost'] || hasBindHost();

			const hasHostIp = () => {
				return hasCommand('hostip');
			};

			const hasNslookup = () => {
				return hasCommand('nslookup');
			};

			res['has_dnsserver'] = cache['has_bindhost'] || hasNslookup() || hasHostIp() || hasBindHost();

			const checkCerts = () => {
				let present = false;
				for (let cert in glob('/etc/ssl/certs/*.crt', '/etc/ssl/certs/*.pem')) {
					if (cert != null)
						present = true;
				}
				return present;
			};

			res['has_cacerts'] = checkCerts();

			res['has_ipv6'] = (stat('/proc/net/ipv6_route')?.type == 'file' && 
				(stat('/usr/sbin/ip6tables')?.type == 'file' || stat('/usr/sbin/nft')?.type == 'file'));

			return res;
		}
	}
};

return { 'luci.ddns': methods };

```

---

# api.js
```javascript
'use strict';
'require rpc';
'require uci';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
LICENSE: GPLv2.0
*/

const callNetworkInterfaceDump = rpc.declare({
	object: 'network.interface',
	method: 'dump',
	expect: { 'interface': [] }
});


let dockerHosts = null;
let dockerHost = null;
let localIPv4 = null;
let localIPv6 = null;
let js_api_available = false;


// Load both UCI config and network interfaces in parallel
const loadPromise = Promise.all([
	callNetworkInterfaceDump(),
	uci.load('dockerd'),
]).then(([interfaceData]) => {

	const lan_device = uci.get('dockerd', 'globals', '_luci_lan') || 'lan';

	// Find local IPs from network interfaces
	if (interfaceData) {
		interfaceData.forEach(iface => {
			// console.log(iface.up)
			if (!iface.up || iface.interface !== lan_device) return;

			// Get IPv4 address
			if (!localIPv4 && iface['ipv4-address']) {
				const addr4 = iface['ipv4-address'].find(a => 
					a.address && !a.address.startsWith('127.')
				);
				if (addr4) localIPv4 = addr4.address;
			}

			// Get IPv6 address
			if (!localIPv6) {
				// Try ipv6-address array first
				if (iface['ipv6-address']) {
					const addr6 = iface['ipv6-address'].find(a =>
						a.address && a.address !== '::1' && !a.address.startsWith('fe80:')
					);
					if (addr6) localIPv6 = addr6.address;
				}

				// Try ipv6-prefix-assignment if no address found
				if (!localIPv6 && iface['ipv6-prefix-assignment']) {
					const prefix = iface['ipv6-prefix-assignment'].find(p =>
						p['local-address'] && p['local-address'].address
					);
					if (prefix) localIPv6 = prefix['local-address'].address;
				}
			}
		});
	}

	dockerHosts = uci.get_first('dockerd', 'globals', 'hosts');

	// Find and convert first tcp:// or tcp6:// host
	const hostsList = Array.isArray(dockerHosts) ? dockerHosts : [];
	const dh = hostsList.find(h => h 
		&& (h.startsWith('tcp://')
			|| h.startsWith('tcp6://')
			|| h.startsWith('inet6://')
			|| h.startsWith('http://')
			|| h.startsWith('https://')
			));

	if (dh) {
		// const isTcp6 = dh.startsWith('tcp6://');
		const protocol = dh.includes(':2376') ? 'https://' : 'http://';
		dockerHost = dh.replace(/^(tcp|inet)6?:\/\//, protocol);

		// Replace 0.0.0.0 or :: with appropriate local IP
		if (localIPv6) {
			dockerHost = dockerHost.replace(/\[::1?\]/, `[${localIPv6}]`);
			// dockerHost = dockerHost.replace(/::/, localIPv6);
		} 

		if (localIPv4) {
			dockerHost = dockerHost.replace(/0\.0\.0\.0/, localIPv4);
		}

		console.log('Docker configured to use JS API to:', dockerHost);
	}

	return dockerHost;
});


// Helper to process NDJSON or line-delimited JSON chunks
function processLines(buffer, onChunk) {
	const lines = buffer.split('\n');
	buffer = lines.pop() || '';
	for (const line of lines) {
		if (line.trim()) {
			try {
				const json = JSON.parse(line);
				onChunk(json);
			} catch (e) {
				onChunk({ raw: line });
			}
		}
	}
	return buffer;
}


function call_docker(method, path, options = {}) {
	return loadPromise.then(() => {
		const headers = { ...(options.headers || {}) };
		const payload = options.payload || null;
		const query = options.query || null;
		const host = dockerHost;
		const onChunk = options.onChunk || null; // Optional callback for streaming NDJSON
		const api_ver = uci.get('dockerd', 'globals', 'api_version') || '';
		const api_ver_str = api_ver ? `/${api_ver}` : '';


		if (!host) {
			return Promise.reject(new Error('Docker host not configured'));
		}

		// Check if WebSocket upgrade is requested
		const isWebSocketUpgrade = headers['Connection']?.toLowerCase() === 'upgrade' || 
									headers['connection']?.toLowerCase() === 'upgrade';

		if (isWebSocketUpgrade) {
			return createWebSocketConnection(host, path, query);
		}

		// Build URL
		let url = `${host}${api_ver_str}${path}`;
		if (query) {
			const params = new URLSearchParams();
			for (const key in query) {
				if (query[key] != null) {
					params.append(key, query[key]);
				}
			}

			// dockerd does not like encoded params here.
			const queryString = params.toString();
			if (queryString) {
				url += `?${queryString}`;
			}
		}

		// Build fetch options
		const fetchOptions = {
			method,
			headers: {
				...headers  // Always include custom headers
			},
		};

		if (payload) {
			fetchOptions.body = JSON.stringify(payload);
			if (!fetchOptions.headers['Content-Type']) {
				fetchOptions.headers['Content-Type'] = 'application/json';
			}
		}

		// Make the request
		return fetch(url, fetchOptions)
			.then(response => {
				// If streaming callback provided, use streaming response
				if (onChunk) {
					const reader = response.body?.getReader();
					const decoder = new TextDecoder();
					let buffer = '';

					return new Promise((resolve) => {
						const processStream = async () => {
							try {
								while (true) {
									const { done, value } = await reader.read();
									
									if (done) {
										// Process any remaining data in buffer
										buffer = processLines(buffer, onChunk);
										break;
									}
									// Decode chunk and add to buffer
									buffer += decoder.decode(value, { stream: true });
									// Use generic processor for NDJSON/line chunks
									buffer = processLines(buffer, onChunk);
								}

								// Return final response
								resolve({
									code: response.status,
									headers: response.headers
								});
							} catch (err) {
								console.error('Streaming error:', err);
								throw err;
							}
						};

						processStream();
					});
				}

				// Normal buffered response
				if (response?.status >= 304) {
					console.error(`HTTP ${response.status}: ${response.statusText}`);
				}

				const headersObj = {};
				for (const [key, value] of response.headers.entries()) {
					headersObj[key] = value;
				}

				return response.text().then(text => {
					const safeText = (typeof text === 'string') ? text : '';
					let parsed = safeText || text;
					const contentType = response.headers.get('content-type') || '';

					// Try normal JSON parse first
					try {
						parsed = JSON.parse(text);
					} catch (err) {
						// If the payload is newline-delimited JSON (Docker events), split and parse each line
						if (['application/json',
							'application/x-ndjson',
							'application/json-seq'].includes(contentType) || safeText.includes('\n')) {
							const lines = safeText.split(/\r?\n/).filter(Boolean);
							try {
								parsed = lines.map(l => JSON.parse(l));
							} catch (err2) {
								// Fall back to raw text if parsing fails
								parsed = text;
							}
						}
					}

					return {
						code: response.status,
						body: parsed,
						headers: headersObj,
					};
				});
			})
			.catch(error => {
				console.error('Docker API error:', error);
			});
	});
}

function createWebSocketConnection(host, path, query) {
	return new Promise((resolve, reject) => {
		try {
			// Convert http/https to ws/wss
			const wsHost = host
				.replace(/^https:/, 'wss:')
				.replace(/^http:/, 'ws:');

			// Build WebSocket URL
			let wsUrl = `${wsHost}${path}`;
			if (query) {
				const params = new URLSearchParams();
				for (const key in query) {
					if (query[key] != null) {
						params.append(key, query[key]);
					}
				}
				const queryString = params.toString();
				if (queryString) {
					wsUrl += `?${queryString}`;
				}
			}

			console.log('Opening WebSocket connection to:', wsUrl);

			const ws = new WebSocket(wsUrl);
			let resolved = false;

			// Handle connection open
			ws.onopen = () => {
				console.log('WebSocket connected');
				if (!resolved) {
					resolved = true;
					// Return a Response-like object with WebSocket support
					resolve({
						ok: true,
						status: 200,
						statusText: 'OK',
						headers: new Map(),
						body: ws,
						ws: ws,
						// Add helper for sending messages
						send: (data) => {
							if (ws.readyState === WebSocket.OPEN) {
								ws.send(data);
							}
						},
						// Add helper for receiving messages as async iterator
						async *[Symbol.asyncIterator]() {
							while (ws.readyState === WebSocket.OPEN) {
								yield new Promise((res, rej) => {
									const messageHandler = (event) => {
										ws.removeEventListener('message', messageHandler);
										ws.removeEventListener('error', errorHandler);
										res(event.data);
									};
									const errorHandler = (error) => {
										ws.removeEventListener('message', messageHandler);
										ws.removeEventListener('error', errorHandler);
										rej(error);
									};
									ws.addEventListener('message', messageHandler);
									ws.addEventListener('error', errorHandler);
								});
							}
						}
					});
				}
			};

			// Handle connection error
			ws.onerror = (error) => {
				console.error('WebSocket error:', error);
				if (!resolved) {
					resolved = true;
					reject(new Error(`WebSocket connection failed: ${error.message || 'Unknown error'}`));
				}
			};

			// Handle close (including handshake failures)
			ws.onclose = (event) => {
				console.log('WebSocket closed');
				if (!resolved) {
					resolved = true;
					reject(new Error(`WebSocket closed before open (${event?.code || 'unknown'})`));
				}
			};

		} catch (error) {
			reject(error);
		}
	});
}


const core_methods = {
	version: { call: () => call_docker('GET', '/version') },
	info:    { call: () => call_docker('GET', '/info') },
	ping:    { call: () => call_docker('GET', '/_ping') },
	df:      { call: () => call_docker('GET', '/system/df') },
	events:  { args: { query: { 'since': '', 'until': `${Date.now()}`, 'filters': '' } }, call: (request) => call_docker('GET', '/events', { query: request?.query, onChunk: request?.onChunk }) },
};

/*
const exec_methods = {
	start:   { args: { id: '', body: '' }, call: (request) => call_docker('POST', `/exec/${request?.id}/start`, { payload: request?.body }) },
	resize:  { args: { id: '', query: { 'h': 0, 'w': 0 } }, call: (request) => call_docker('POST', `/exec/${request?.id}/resize`, { query: request?.query }) },
	inspect: { args: { id: '' }, call: (request) => call_docker('GET', `/exec/${request?.id}/json`) },
};
*/

const container_methods = {
	list:    { args: { query: { 'all': false, 'limit': false, 'size': false, 'filters': '' } }, call: (request) => call_docker('GET', '/containers/json', { query: request?.query }) },
	create:  { args: { query: { 'name': '', 'platform': '' }, body: {} }, call: (request) => call_docker('POST', '/containers/create', { query: request?.query, payload: request?.body }) },
	inspect: { args: { id: '', query: { 'size': false } }, call: (request) => call_docker('GET', `/containers/${request?.id}/json`, { query: request?.query }) },
	top:     { args: { id: '', query: { 'ps_args': '' } }, call: (request) => call_docker('GET', `/containers/${request?.id}/top`, { query: request?.query }) },
	logs:    { args: { id: '', query: {} }, call: (request) => call_docker('GET', `/containers/${request?.id}/logs`, { query: request?.query, onChunk: request?.onChunk }) },
	changes: { args: { id: '' }, call: (request) => call_docker('GET', `/containers/${request?.id}/changes`) },
	export:  { args: { id: '' }, call: (request) => call_docker('GET', `/containers/${request?.id}/export`) },
	stats:   { args: { id: '', query: { 'stream': false, 'one-shot': false } }, call: (request) => call_docker('GET', `/containers/${request?.id}/stats`, { query: request?.query }) },
	resize:  { args: { id: '', query: { 'h': 0, 'w': 0 } }, call: (request) => call_docker('POST', `/containers/${request?.id}/resize`, { query: request?.query }) },
	start:   { args: { id: '', query: { 'detachKeys': '' } }, call: (request) => call_docker('POST', `/containers/${request?.id}/start`, { query: request?.query }) },
	stop:    { args: { id: '', query: { 'signal': '', 't': 0 } }, call: (request) => call_docker('POST', `/containers/${request?.id}/stop`, { query: request?.query }) },
	restart: { args: { id: '', query: { 'signal': '', 't': 0 } }, call: (request) => call_docker('POST', `/containers/${request?.id}/restart`, { query: request?.query }) },
	kill:    { args: { id: '', query: { 'signal': '' } }, call: (request) => call_docker('POST', `/containers/${request?.id}/kill`, { query: request?.query }) },
	update:  { args: { id: '', body: {} }, call: (request) => call_docker('POST', `/containers/${request?.id}/update`, { payload: request?.body }) },
	rename:  { args: { id: '', query: { 'name': '' } }, call: (request) => call_docker('POST', `/containers/${request?.id}/rename`, { query: request?.query }) },
	pause:   { args: { id: '' }, call: (request) => call_docker('POST', `/containers/${request?.id}/pause`) },
	unpause: { args: { id: '' }, call: (request) => call_docker('POST', `/containers/${request?.id}/unpause`) },
	// attach
	// attach websocket
	attach_ws: { args: { id: '' }, call: (request) => call_docker('GET', `/containers/${request?.id}/attach/ws`, { query: request?.query, headers: { 'Connection': 'Upgrade' } }) },
	// wait
	remove:  { args: { id: '', query: { 'v': false, 'force': false, 'link': false } }, call: (request) => call_docker('DELETE', `/containers/${request?.id}`, { query: request?.query }) },
	// archive info
	info_archive: { args: { id: '', query: { 'path': '' } }, call: (request) => call_docker('HEAD', `/containers/${request?.id}/archive`, { query: request?.query }) },
	// archive get
	get_archive:  { args: { id: '', query: { 'path': '' } }, call: (request) => call_docker('GET', `/containers/${request?.id}/archive`, { query: request?.query }) },
	// archive extract
	put_archive:  { args: { id: '', query: { 'path': '', 'noOverwriteDirNonDir': '', 'copyUIDGID': '' }, body: '' }, call: (request) => call_docker('PUT', `/containers/${request?.id}/archive`, { query: request?.query, payload: request?.body }) },
	exec:    { args: { id: '', opts: {} }, call: (request) => call_docker('POST', `/containers/${request?.id}/exec`, { payload: request?.opts }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/containers/prune', { query: request?.query }) },

	// Not a docker command - but a local command to invoke ttyd so our browser can open websocket to docker
	// ttyd_start: { args: { id: '', cmd: '/bin/sh', port: 7682, uid: '' }, call: (request) => run_ttyd(request) },

};


const image_methods = {
	list:    { args: { query: { 'all': false, 'digests': false, 'shared-size': false, 'manifests': false, 'filters': '' } }, call: (request) => call_docker('GET', '/images/json', { query: request?.query }) },
	build:  { args: { query: { '': '' }, headers: {}, onChunk: null }, call: (request) => call_docker('POST', '/build', { query: request?.query, headers: request?.headers, onChunk: request?.onChunk }) },
	build_prune:  { args: { query: { '': '' }, headers: {}, onChunk: null }, call: (request) => call_docker('POST', '/build/prune', { query: request?.query, headers: request?.headers, onChunk: request?.onChunk }) },
	create:  { args: { query: { '': '' }, headers: {}, onChunk: null }, call: (request) => call_docker('POST', '/images/create', { query: request?.query, headers: request?.headers, onChunk: request?.onChunk }) },
	inspect: { args: { id: '' }, call: (request) => call_docker('GET', `/images/${request?.id}/json`) },
	history: { args: { id: '' }, call: (request) => call_docker('GET', `/images/${request?.id}/history`) },
	push:    { args: { name: '', query: { tag: '', platform: '' }, headers: {}, onChunk: null }, call: (request) => call_docker('POST', `/images/${request?.name}/push`, { query: request?.query, headers: request?.headers, onChunk: request?.onChunk }) },
	tag:     { args: { id: '', query: { 'repo': '', 'tag': '' } }, call: (request) => call_docker('POST', `/images/${request?.id}/tag`, { query: request?.query }) },
	remove:  { args: { id: '', query: { 'force': false, 'noprune': false }, onChunk: null }, call: (request) => call_docker('DELETE', `/images/${request?.id}`, { query: request?.query, onChunk: request?.onChunk }) },
	search:  { args: { query: { 'term': '', 'limit': 0, 'filters': '' } }, call: (request) => call_docker('GET', '/images/search', { query: request?.query }) },
	prune:   { args: { query: { 'filters': '' }, onChunk: null }, call: (request) => call_docker('POST', '/images/prune', { query: request?.query, onChunk: request?.onChunk }) },
	// create/commit
	get:     { args: { id: '', onChunk: null }, call: (request) => call_docker('GET', `/images/${request?.id}/get`, { onChunk: request?.onChunk }) },
	// get == export several
	load:    { args: { query: { 'quiet': false }, onChunk: null }, call: (request) => call_docker('POST', '/images/load', { query: request?.query, onChunk: request?.onChunk }) },
};


const network_methods = {
	list:    { args: { query: { 'filters': '' } }, call: (request) => call_docker('GET', '/networks', { query: request?.query }) },
	inspect: { args: { id: '', query: { 'verbose': false, 'scope': '' } }, call: (request) => call_docker('GET', `/networks/${request?.id}`, { query: request?.query }) },
	remove:  { args: { id: '' }, call: (request) => call_docker('DELETE', `/networks/${request?.id}`) },
	create:  { args: { body: {} }, call: (request) => call_docker('POST', '/networks/create', { payload: request?.body }) },
	connect: { args: { id: '', body: {} }, call: (request) => call_docker('POST', `/networks/${request?.id}/connect`, { payload: request?.body }) },
	disconnect: { args: { id: '', body: {} }, call: (request) => call_docker('POST', `/networks/${request?.id}/disconnect`, { payload: request?.body }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/networks/prune', { query: request?.query }) },
};


const volume_methods = {
	list:    { args: { query: { 'filters': '' } }, call: (request) => call_docker('GET', '/volumes', { query: request?.query }) },
	create:  { args: { opts: {} }, call: (request) => call_docker('POST', '/volumes/create', { payload: request?.opts }) },
	inspect: { args: { id: '' }, call: (request) => call_docker('GET', `/volumes/${request?.id}`) },
	update:  { args: { id: '', query: { 'version': 0 }, spec: {} }, call: (request) => call_docker('PUT', `/volumes/${request?.id}`, { query: request?.query, payload: request?.spec }) },
	remove:  { args: { id: '', query: { 'force': false } }, call: (request) => call_docker('DELETE', `/volumes/${request?.id}`, { query: request?.query }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/volumes/prune', { query: request?.query }) },
};


// const methods = {
// 	'docker': core_methods, 
// 	'docker.container': container_methods,
// 	'docker.exec': exec_methods,
// 	'docker.image': image_methods,
// 	'docker.network': network_methods,
// 	'docker.volume': volume_methods,
// };


// Determine JS API availability after core methods are ready
const apiAvailabilityPromise = loadPromise.then(() => {
	if (!dockerHost) {
		js_api_available = false;
		return [js_api_available, dockerHost];
	}

	return core_methods.ping.call()
		.then(res => {
			// ping returns raw 'OK' text; treat any truthy/OK as success
			const body = res?.body;
			js_api_available = body === 'OK';
			return [js_api_available, dockerHost];
		})
		.catch(error => {
			console.warn('JS API unavailable (likely CORS or network):', error?.message || error);
			js_api_available = false;
			return [js_api_available, dockerHost];
		});
});


return L.Class.extend({
	js_api_available: () => apiAvailabilityPromise.then(() => [js_api_available, dockerHost]),
	container_attach_ws: container_methods.attach_ws.call,
	container_changes: container_methods.changes.call,
	container_create: container_methods.create.call,
	// container_export: container_export, // use controller instead
	container_info_archive: container_methods.info_archive.call,
	container_inspect: container_methods.inspect.call,
	container_kill: container_methods.kill.call,
	container_list: container_methods.list.call,
	container_logs: container_methods.logs.call,
	container_pause: container_methods.pause.call,
	container_prune: container_methods.prune.call,
	container_remove: container_methods.remove.call,
	container_rename: container_methods.rename.call,
	container_restart: container_methods.restart.call,
	container_start: container_methods.start.call,
	container_stats: container_methods.stats.call,
	container_stop: container_methods.stop.call,
	container_top: container_methods.top.call,
	// container_ttyd_start: container_methods.ttyd_start.call,
	container_unpause: container_methods.unpause.call,
	container_update: container_methods.update.call,
	docker_version: core_methods.version.call,
	docker_info: core_methods.info.call,
	docker_ping: core_methods.ping.call,
	docker_df: core_methods.df.call,
	docker_events: core_methods.events.call,
	image_build: image_methods.build.call,
	image_create: image_methods.create.call,
	image_history: image_methods.history.call,
	image_inspect: image_methods.inspect.call,
	image_list: image_methods.list.call,
	image_prune: image_methods.prune.call,
	image_push: image_methods.push.call,
	image_remove: image_methods.remove.call,
	image_tag: image_methods.tag.call,
	network_connect: network_methods.connect.call,
	network_create: network_methods.create.call,
	network_disconnect: network_methods.disconnect.call,
	network_inspect: network_methods.inspect.call,
	network_list: network_methods.list.call,
	network_prune: network_methods.prune.call,
	network_remove: network_methods.remove.call,
	volume_create: volume_methods.create.call,
	volume_inspect: volume_methods.inspect.call,
	volume_list: volume_methods.list.call,
	volume_prune: volume_methods.prune.call,
	volume_remove: volume_methods.remove.call,

});


```

---

# common.js
```javascript
'use strict';
'require form';
'require fs';
'require uci';
'require ui';
'require rpc';
'require view';
'require dockerman.api as jsapi';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
LICENSE: GPLv2.0
*/

// docker df endpoint can take a while to resolve everything on *big* docker setups
// L.env.timeout = 40;

// Start docker API RPC methods

// If you define new declarations here, remember to export them at the bottom.
const container_changes = rpc.declare({
	object: 'docker.container',
	method: 'changes',
	params: { id: '' },
});

const container_create = rpc.declare({
	object: 'docker.container',
	method: 'create',
	params: { query: { }, body: { } },
});

/* We don't use rpcd for export functions, use controller instead
const container_export = rpc.declare({
	object: 'docker.container',
	method: 'export',
	params: { id: '' },
});
*/

const container_info_archive = rpc.declare({
	object: 'docker.container',
	method: 'info_archive',
	params: { id: '', query: { path: '/' } },
});

const container_inspect = rpc.declare({
	object: 'docker.container',
	method: 'inspect',
	params: { id: '', query: { } },
});

const container_kill = rpc.declare({
	object: 'docker.container',
	method: 'kill',
	params: { id: '', query: { } },
});

const container_list = rpc.declare({
	object: 'docker.container',
	method: 'list',
	params: { query: { } },
});

const container_logs = rpc.declare({
	object: 'docker.container',
	method: 'logs',
	params: { id: '', query: { } },
});

const container_pause = rpc.declare({
	object: 'docker.container',
	method: 'pause',
	params: { id: '' },
});

const container_prune = rpc.declare({
	object: 'docker.container',
	method: 'prune',
	params: { query: { } },
});

const container_remove = rpc.declare({
	object: 'docker.container',
	method: 'remove',
	params: { id: '', query: { } },
});

const container_rename = rpc.declare({
	object: 'docker.container',
	method: 'rename',
	params: { id: '', query: { } },
});

const container_restart = rpc.declare({
	object: 'docker.container',
	method: 'restart',
	params: { id: '', query: { } },
});

const container_start = rpc.declare({
	object: 'docker.container',
	method: 'start',
	params: { id: '', query: { } },
});

const container_stats = rpc.declare({
	object: 'docker.container',
	method: 'stats',
	params: { id: '', query: { 'stream': false, 'one-shot': true } },
});

const container_stop = rpc.declare({
	object: 'docker.container',
	method: 'stop',
	params: { id: '', query: { } },
});

const container_top = rpc.declare({
	object: 'docker.container',
	method: 'top',
	params: { id: '', query: { 'ps_args': '' } },
});

const container_unpause = rpc.declare({
	object: 'docker.container',
	method: 'unpause',
	params: { id: '' },
});

const container_update = rpc.declare({
	object: 'docker.container',
	method: 'update',
	params: { id: '', body: { } },
});

const container_ttyd_start = rpc.declare({
	object: 'docker.container',
	method: 'ttyd_start',
	params: { id: '', cmd: '/bin/sh', port: 7682, uid: '' },
});

// Data Usage
const docker_df = rpc.declare({
	object: 'docker',
	method: 'df',
});

const docker_events = rpc.declare({
	object: 'docker',
	method: 'events',
	params: { query: { since: '', until: '', filters: '' } }
});

const docker_info = rpc.declare({
	object: 'docker',
	method: 'info',
});

const docker_version = rpc.declare({
	object: 'docker',
	method: 'version',
});

/* We don't use rpcd for import/build functions, use controller instead
const image_build = rpc.declare({
	object: 'docker.image',
	method: 'build',
	params: { query: { }, headers: { } },
});
*/

const image_create = rpc.declare({
	object: 'docker.image',
	method: 'create',
	params: { query: { }, headers: { } },
});

/* We don't use rpcd for export functions, use controller instead
const image_get = rpc.declare({
	object: 'docker.image',
	method: 'get',
	params: { id: '', query: { } },
});
*/

const image_history = rpc.declare({
	object: 'docker.image',
	method: 'history',
	params: { id: '' },
});

const image_inspect = rpc.declare({
	object: 'docker.image',
	method: 'inspect',
	params: { id: '' },
});

const image_list = rpc.declare({
	object: 'docker.image',
	method: 'list',
});

const image_prune = rpc.declare({
	object: 'docker.image',
	method: 'prune',
	params: { query: { } },
});

const image_push = rpc.declare({
	object: 'docker.image',
	method: 'push',
	params: { name: '', query: { }, headers: { } },
});

const image_remove = rpc.declare({
	object: 'docker.image',
	method: 'remove',
	params: { id: '', query: { } },
});

const image_tag = rpc.declare({
	object: 'docker.image',
	method: 'tag',
	params: { id: '', query: { } },
});

const network_connect = rpc.declare({
	object: 'docker.network',
	method: 'connect',
	params: { id: '', body: {} },
});

const network_create = rpc.declare({
	object: 'docker.network',
	method: 'create',
	params: { body: {} },
});

const network_disconnect = rpc.declare({
	object: 'docker.network',
	method: 'disconnect',
	params: { id: '', body: {} },
});

const network_inspect = rpc.declare({
	object: 'docker.network',
	method: 'inspect',
	params: { id: '' },
});

const network_list = rpc.declare({
	object: 'docker.network',
	method: 'list',
});

const network_prune = rpc.declare({
	object: 'docker.network',
	method: 'prune',
	params: { query: { } },
});

const network_remove = rpc.declare({
	object: 'docker.network',
	method: 'remove',
	params: { id: '' },
});

const volume_create = rpc.declare({
	object: 'docker.volume',
	method: 'create',
	params: { opts: {} },
});

const volume_inspect = rpc.declare({
	object: 'docker.volume',
	method: 'inspect',
	params: { id: '' },
});

const volume_list = rpc.declare({
	object: 'docker.volume',
	method: 'list',
});

const volume_prune = rpc.declare({
	object: 'docker.volume',
	method: 'prune',
	params: { query: { } },
});

const volume_remove = rpc.declare({
	object: 'docker.volume',
	method: 'remove',
	params: { id: '', query: { } },
});

// End docker API RPC methods

const callMountPoints = rpc.declare({
	object: 'luci',
	method: 'getMountPoints',
	expect: { result: [] }
});


const callRcInit = rpc.declare({
	object: 'rc',
	method: 'init',
	params: [ 'name', 'action' ],
});

// End generic API methods


const builder = Object.freeze({
	prune: {e: '✂️', i18n: _('prune')},
});


const container = Object.freeze({
	attach: {e: '🔌', i18n: _('attach')},
	commit: {e: '🎯', i18n: _('commit')},
	copy: {e: '📃➡️📃', i18n: _('copy')},
	create: {e: '➕', i18n: _('create')},
	destroy: {e: '💥', i18n: _('destroy')},
	detach: {e: '❌🔌', i18n: _('detach')},
	die: {e: '🪦', i18n: _('die')},
	exec_create: {e: '➕', i18n: _('exec_create')},
	exec_detach: {e: '❌🔌', i18n: _('exec_detach')},
	exec_start: {e: '▶️', i18n: _('exec_start')},
	exec_die: {e: '🪦', i18n: _('exec_die')},
	export: {e: '📤⬇️', i18n: _('export')},
	health_status: {e: '🩺⚕️', i18n: _('health_status')},
	kill: {e: '☠️', i18n: _('kill')},
	oom: {e: '0️⃣🧠', i18n: _('oom')},
	pause: {e: '⏸️', i18n: _('pause')},
	rename: {e: '✍️', i18n: _('rename')},
	resize: {e: '↔️', i18n: _('resize')},
	restart: {e: '🔄', i18n: _('restart')},
	start: {e: '▶️', i18n: _('start')},
	stop: {e: '⏹️', i18n: _('stop')},
	top: {e: '🔝', i18n: _('top')},
	unpause: {e: '⏯️', i18n: _('unpause')},
	update: {e: '✏️', i18n: _('update')},
	prune: {e: '✂️', i18n: _('prune')},
});


const daemon = Object.freeze({
	reload: {e: '🔄', i18n: _('reload')},
});


const image = Object.freeze({
	create: {e: '➕', i18n: _('create')},
	delete: {e: '❌', i18n: _('delete')},
	import: {e: '➡️', i18n: _('Import')},
	load: {e: '⬆️', i18n: _('load')},
	pull: {e: '☁️⬇️', i18n: _('Pull')},
	push: {e: '☁️⬆️', i18n: _('Push')},
	save: {e: '💾', i18n: _('save')},
	tag: {e: '🏷️', i18n: _('tag')},
	untag: {e: '❌🏷️', i18n: _('untag')},
	prune: {e: '✂️', i18n: _('prune')},
});


const network = Object.freeze({
	create: {e: '➕', i18n: _('create')},
	connect: {e: '🔗', i18n: _('connect')},
	disconnect: {e: '⛓️‍💥', i18n: _('disconnect')},
	destroy: {e: '💥', i18n: _('destroy')},
	update: {e: '✏️', i18n: _('update')},
	remove: {e: '❌', i18n: _('remove')},
	prune: {e: '✂️', i18n: _('prune')},
});


const volume = Object.freeze({
	create: {e: '➕', i18n: _('create')},
	mount: {e: '⬆️', i18n: _('mount')},
	unmount: {e: '⬇️', i18n: _('unmount')},
	destroy: {e: '💥', i18n: _('destroy')},
	prune: {e: '✂️', i18n: _('prune')},
});


const CURTypes = Object.freeze({
	create: {e: '➕', i18n: _('create')},
	update: {e: '✏️', i18n: _('update')},
	remove: {e: '❌', i18n: _('remove')},
});


const config = CURTypes;
const node = CURTypes;
const secret = CURTypes;
const service = CURTypes;


const Types = Object.freeze({
	builder: {e: '🛠️', i18n: _('builder'), sub: builder},
	config: {e: '⚙️', i18n: _('config'), sub: config},
	container: {e: '🐳', i18n: _('container'), sub: container},
	daemon: {e: '🔁', i18n: _('daemon'), sub: daemon},
	image: {e: '🌄', i18n: _('image'), sub: image},
	network: {e: '모', i18n: _('network'), sub: network },
	node: {e: '✳️', i18n: _('node'), sub: node },
	plugin: {e: '🔌', i18n: _('plugin') },
	secret: {e: '🔐', i18n: _('secret'), sub: secret },
	service: {e: '🛎️', i18n: _('service'), sub: service },
	volume: {e: '💿', i18n: _('volume'), sub: volume},
});


const ActionTypes = Object.freeze({
	build: {e: '🏗️', i18n: _('Build')},
	clean: {e: '🧹', i18n: _('Clean')},
	create: {e: '🪄➕', i18n: _('Create')},
	edit: {e: '✏️', i18n: _('Edit')},
	force_remove: {e: '❌', i18n: _('Force remove')},
	history: {e: '🪶📜', i18n: _('History')},
	inspect: {e: '🔎', i18n: _('Inspect') },
	remove: {e: '❌', i18n: _('Remove')},
	save: {e: '⬇️', i18n: _('Save locally')},
	upload: {e: '⬆️', i18n: _('Upload')},
	prune: {e: '✂️', i18n: _('Prune')},
});


const ignored_headers = ['cache-control', 'connection', 'content-length', 'content-type', 'pragma',
	'Components', 'Platform'];

const dv = view.extend({
	outputText: '', // Initialize output text

	get dockerman_url() {
		return L.url('admin/services/dockerman');
	},

	parseHeaders(headers, array) {
		for(const [k, v] of Object.entries(headers)) {
			if (ignored_headers.includes(k)) continue;
			array.push({entry: k, value: v});
		}
	},

	parseBody(body, array) {
		for(const [k, v] of Object.entries(body)) {
			if (ignored_headers.includes(k)) continue;
			if (!v) continue;
			array.push({entry: k, value: (typeof v !== 'string') ? JSON.stringify(v) : v});
		}
	},

	rwxToMode(val) {
		if (!val) return undefined;
		const raw = String(val).trim();
		if (/^[0-7]+$/.test(raw)) return parseInt(raw, 8);
		const normalized = raw.replace(/[^rwx-]/gi, '').padEnd(9, '-').slice(0, 9);
		const chunkToNum = (chunk) => (
			(chunk[0] === 'r' ? 4 : 0) +
			(chunk[1] === 'w' ? 2 : 0) +
			(chunk[2] === 'x' ? 1 : 0)
		);
		const owner = chunkToNum(normalized.slice(0, 3));
		const group = chunkToNum(normalized.slice(3, 6));
		const other = chunkToNum(normalized.slice(6, 9));
		return (owner << 6) + (group << 3) + other;
	},

	modeToRwx(mode) {
		const perms = mode & 0o777; // extract permission bits

		const toRwx = n => 
			((n & 4) ? 'r' : '-') +
			((n & 2) ? 'w' : '-') +
			((n & 1) ? 'x' : '-');

		const owner = toRwx((perms >> 6) & 0b111);
		const group = toRwx((perms >> 3) & 0b111);
		const world = toRwx(perms & 0b111);

		return `${owner}${group}${world}`;
	},

	parseMemory(value) {
		if (!value) return 0;
		const rex = /^([0-9.]+) *([bkmgt])?i? *[Bb]?/i;
		let [, amount, unit] = rex.exec(value.toLowerCase());
		amount = amount ? Number.parseFloat(amount) : 0;
		switch (unit) {
		default: break;
		case 'k': amount *= (2 ** 10); break;
		case 'm': amount *= (2 ** 20); break;
		case 'g': amount *= (2 ** 30); break;
		case 't': amount *= (2 ** 40); break;
		case 'p': amount *= (2 ** 50); break;
		}
		return amount;
	},

	listToKv: (list) => {
		const kv = {};
		const items = Array.isArray(list) ? list : (list != null ? [list] : []);
		items.forEach((entry) => {
			if (typeof entry !== 'string')
				return;

			const pos = entry.indexOf('=');
			if (pos <= 0)
				return;

			const key = entry.slice(0, pos);
			const val = entry.slice(pos + 1);
			if (key)
				kv[key] = val;
		});
		return kv;
	},

	objectToText(object) {
		let result = '';
		if (!object || typeof object !== 'object') return result;
		if (Object.keys(object).length === 0) return result;
		for (const [k, v] of Object.entries(object))
			result += `${!result ? '' : ', '}${k}: ${typeof v === 'object' ? this.objectToText(v) : v}`
		return result;
	},

	objectCfgValueTT(sid) {
		const val = this.data?.[sid] ?? this.map.data.get(this.map.config, sid, this.option);
		return (val != null && typeof val === 'object') ? dv.prototype.objectToText.call(dv.prototype, val) : val;
	},

	insertOutputFrame(s, m) {
		const frame = E('div', {
				'class': 'cbi-section'
			}, [
				E('h3', {}, _('Operational Output')),
				E('textarea', {
					'readonly': true,
					'rows': 30,
					'style': 'width: 100%; font-family: monospace;',
					'id': 'inspect-output-text'
				}, this.outputText)
			]);
		if (!m) return frame;
		// Output section, for inspect results
		s = m.section(form.NamedSection, null, 'inspect');
		s.anonymous = true;
		s.render = L.bind(() => {
			return frame;
		}, this);
	},

	insertOutput(text) {
		// send text to the output text-area and scroll to bottom
		this.outputText = text;
		const textarea = document.getElementById('inspect-output-text');
		if (textarea) {
			textarea.value = this.outputText;
			textarea.scrollTop = textarea.scrollHeight;
		}
	},

	buildTimeString(unixtime) {
		return new Date(unixtime * 1000).toLocaleDateString([], {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		});
	},

	buildNetworkListValues(networks, option) {
		for (const network of networks) {
			let name = `${network?.Name}`;
			name += network?.Driver ? ` | ${network?.Driver}` : '';
			name += network?.IPAM?.Config?.[0] ? ` | ${network?.IPAM?.Config?.[0]?.Subnet}` : '';
			name += network?.IPAM?.Config?.[1] ? ` | ${network?.IPAM?.Config?.[1]?.Subnet}` : '';
			option.value(network?.Name, name);
		}
	},

	getContainerStatus(this_container) {
		if (!this_container?.State)
			return 'unknown';
		const state = this_container.State;
		if (state.Status === 'paused')
			return 'paused';
		else if (state.Running && !state.Restarting)
			return 'running';
		else if (state.Running && state.Restarting)
			return 'restarting';
		return 'stopped';
	},

	getImageFirstTag(image_list, image_id) {
		const imageArray = Array.isArray(image_list) ? image_list : [];
		const imageInfo = imageArray.find(img => img?.Id === image_id);
		const imageName = imageInfo && Array.isArray(imageInfo.RepoTags) 
			? imageInfo.RepoTags[0] 
			: 'unknown';
		return imageName;
	},

	parseNetworkLinksForContainer(networks, containerNetworks, name_links) {
		const links = [];

		if (!Array.isArray(containerNetworks)) {
			if (containerNetworks && typeof containerNetworks === 'object')
				containerNetworks = Object.values(containerNetworks);
		}

		for (const cNet of containerNetworks) {
			const network = networks.find(n => 
				n.Name === cNet.Name || 
				n.Id === cNet?.NetworkID ||
				n.Id === cNet.Name
			);

			if (network) {
				links.push(E('a', {
					href: `${this.dockerman_url}/network/${network.Id}`,
					title: network.Id,
					style: 'white-space: nowrap;'
				}, [name_links ? network.Name : network.Id.slice(0,12)]));
			}
		}

		if (!links.length)
			return '-';

		// Join with pipes
		const out = [];
		for (let i = 0; i < links.length; i++) {
			out.push(links[i]);
			if (i < links.length - 1)
				out.push(' | ');
		}

		return E('div', {}, out);
	},

	parseContainerLinksForNetwork(network, containers) {
		// Find all containers connected to this network
		const containerLinks = [];
		for (const cont of containers) {
			let isConnected = false;
			if (cont.NetworkSettings?.Networks?.[network?.Name]) {
				isConnected = true;
			}
			else
			if (cont.NetworkSettings?.Networks?.[network?.Id]) {
				isConnected = true;
			}

			if (isConnected) {
				const containerName = cont.Names?.[0]?.replace(/^\//, '') || cont.Id?.substring(0, 12);
				const containerId = cont.Id;

				containerLinks.push(E('a', {
					href: `${this.dockerman_url}/container/${containerId}`,
					title: containerId,
					style: 'white-space: nowrap;'
				}, [containerName]));
			}
		}

		if (!containerLinks.length)
			return '-';

		// Join with pipes
		const out = [];
		for (let i = 0; i < containerLinks.length; i++) {
			out.push(containerLinks[i]);
			if (i < containerLinks.length - 1)
				out.push(' | ');
		}

		return E('div', {}, out);
	},

	statusColor(status) {
		const s = (status || '').toLowerCase();
		if (s === 'running') return '#2ecc71'; // green
		if (s === 'paused') return '#f39c12'; // orange
		if (s === 'restarting') return '#f39c12'; // orange
		return '#d9534f'; // red for stopped/other
	},

	wrapStatusText(text, status, extraStyle = '') {
		const color = this.statusColor(status);
		return E('span', { style: `color:${color};${extraStyle || ''}` }, [text]);
	},

	/**
	 * Show a notification to the user with standardized formatting
	 * @param {string} title - The title of the notification (will be translated if needed)
	 * @param {string|Array<string>} message - Message(s) to display
	 * @param {number} [duration=5000] - Duration in milliseconds
	 * @param {string} [type='info'] - Type: 'success', 'info', 'warning', 'error'
	 */
	showNotification(title, message, duration = 5000, type = 'info') {
		const messages = Array.isArray(message) ? message : [message];
		ui.addTimeLimitedNotification(title, messages, duration, type);
	},

	/**
	 * Normalize a registry host address by stripping scheme and path
	 * @param {string} address - The registry address to normalize
	 * @returns {string|null} - Normalized hostname or null
	 */
	normalizeRegistryHost(address) {
		if (!address) return null;

		let addr = String(address).trim();
		// make exception for legacy Docker Hub registry https://index.docker.io/v1/
		if (addr.includes('index.docker.io'))
			return addr.toLowerCase();
		else {
			addr = addr.replace(/^[a-z]+:\/\//i, '');
			addr = addr.split('/')[0];
			addr = addr.replace(/\/$/, '');
		}
		if (!addr) return null;
		return addr.toLowerCase();
	},

	/**
	 * Ensure registry address has https:// scheme
	 * @param {string} address - The registry address
	 * @param {string} hostFallback - Fallback host if address is empty
	 * @returns {string|null} - Address with scheme or null
	 */
	ensureRegistryScheme(address, hostFallback) {
		const addr = String(address || '').trim() || hostFallback;
		if (!addr) return null;
		/* jsmin cannot handle /^https?:\/\//i.test(addr) - wrap in parentheses: OK
		https = new RegExp('https?:\/\/', 'i'); // also OK
		 */
		return (/^https?:\/\//i.test(addr)) ? addr : `https://${addr}`;
	},

	/**
	 * Encode auth object to base64
	 * @param {Object} obj - Object with username, password, serveraddress
	 * @returns {string|null} - Base64 encoded JSON or null on failure
	 */
	encodeBase64Json(obj) {
		const json = JSON.stringify(obj);
		try {
			return btoa(json);
		} catch (err) {
			try {
				return btoa(unescape(encodeURIComponent(json)));
			} catch (err2) {
				console.warn('Failed to encode registry auth', err2?.message || err2);
				return null;
			}
		}
	},

	/**
	 * Extract registry host from image tag
	 * @param {string} tag - The image tag
	 * @returns {string|null} - Registry hostname or null
	 */
	extractRegistryHostFromImage(tag) {
		if (!tag) return null;

		let ref = String(tag).trim();
		ref = ref.replace(/^[a-z]+:\/\//i, '');

		const slashIdx = ref.indexOf('/');
		const candidate = slashIdx === -1 ? ref : ref.slice(0, slashIdx);
		if (!candidate) return null;

		const hasDot = candidate.includes('.');
		const hasPort = /:[0-9]+$/.test(candidate);
		const isLocal = candidate === 'localhost' || candidate.startsWith('localhost:');
		if (!hasDot && !hasPort && !isLocal) return null;

		return candidate.toLowerCase();
	},

	/**
	 * Resolve registry credentials and build auth header
	 * @param {string} imageRef - The image reference
	 * @param {Map} registryAuthMap - Map of registry host to credentials
	 * @returns {string|null} - Base64 encoded auth string or null
	 */
	resolveRegistryAuth(imageRef, registryAuthMap) {
		const host = this.extractRegistryHostFromImage(imageRef);
		if (!host) return null;

		const creds = registryAuthMap.get(host);
		if (!creds?.username || !creds?.password) return null;

		return this.encodeBase64Json({
			username: creds.username,
			password: creds.password,
			serveraddress: this.ensureRegistryScheme(creds.serveraddress, host)
		});
	},

	/**
	 * Load registry auth credentials from UCI config
	 * @returns {Promise<Map>} - Promise resolving to Map of registry host to credentials
	 */
	loadRegistryAuthMap() {
		return new Promise((resolve) => {
			// Load UCI and extract auth sections
			const authMap = new Map();
			L.resolveDefault(uci.load('dockerd'), {}).then(() => {
				uci.sections('dockerd', 'auth', (section) => {
					const serverRaw = section?.serveraddress;
					const host = this.normalizeRegistryHost(serverRaw);
					if (!host) return;

					const username = section?.username || section?.user;
					const password = section?.token || section?.password;
					if (!username || !password) return;

					authMap.set(host, {
						username,
						password,
						serveraddress: serverRaw || host,
					});
				});
				resolve(authMap);
			}).catch(() => {
				// If loading fails, return empty map
				resolve(authMap);
			});
		});
	},

	/**
	 * Handle Docker API response with unified error checking and user feedback
	 * @param {Object} response - The Docker API response object
	 * @param {string} actionName - Name of the action (e.g., 'Start', 'Remove')
	 * @param {Object} [options={}] - Optional configuration
	 * @param {boolean} [options.showOutput=true] - Whether to insert JSON output
	 * @param {boolean} [options.showSuccess=true] - Whether to show success notification
	 * @param {string} [options.successMessage] - Custom success message
	 * @param {number} [options.successDuration=4000] - Success notification duration
	 * @param {number} [options.errorDuration=7000] - Error notification duration
	 * @param {Function} [options.onSuccess] - Callback on success
	 * @param {Function} [options.onError] - Callback on error
	 * @param {Object} [options.specialCases] - Map of status codes to handlers {304: {message: '...', type: 'notice'}}
	 * @returns {boolean} - true if successful, false otherwise
	 */
	handleDockerResponse(response, actionName, options = {}) {
		const {
			showOutput = true,
			showSuccess = true,
			successMessage = _('OK'),
			successDuration = 4000,
			errorDuration = 7000,
			onSuccess = null,
			onError = null,
			specialCases = {}
		} = options;

		// Handle special status codes first (e.g., 304 Not Modified)
		if (specialCases[response?.code]) {
			const special = specialCases[response.code];
			this.showNotification(
				actionName,
				special.message || _('No changes needed'),
				special.duration || 5000,
				special.type || 'notice'
			);
			if (onSuccess) onSuccess(response);
			return true;
		}

		// Insert output if requested
		if (showOutput && response?.body != null) {
			const outputText = response?.body !== "" 
				? (Array.isArray(response.body) || typeof response.body === 'object' 
					? JSON.stringify(response.body, null, 2) + '\n' 
					: String(response.body) + '\n')
				: `${response?.code} ${_('OK')}\n`;
			this.insertOutput(outputText);
		}

		// Check for errors (HTTP status >= 304)
		if (response?.code >= 304) {
			this.showNotification(
				actionName,
				response?.body?.message || _('Operation failed'),
				errorDuration,
				'warning'
			);
			if (onError) onError(response);
			return false;
		}

		// Success case
		if (showSuccess) {
			this.showNotification(actionName, successMessage, successDuration, 'success');
		}
		if (onSuccess) onSuccess(response);
		return true;
	},

	async getRegistryAuth(params, actionName) {
		// Extract registry candidate from params
		let registryCandidate = null;
		if (params?.query?.fromImage) {
			registryCandidate = params.query.fromImage;
		} else if (params?.query?.tag) {
			registryCandidate = params.query.tag;
		}

		if (params?.name && actionName === Types['image'].sub['push'].i18n) {
			registryCandidate = params.name;
		}

		// Try to load and inject registry auth if we have a registry candidate
		if (registryCandidate) {
			try {
				const authMap = await this.loadRegistryAuthMap();
				const auth = this.resolveRegistryAuth(registryCandidate, authMap);
				if (auth) {
					if (!params.headers) {
						params.headers = {};
					}
					params.headers['X-Registry-Auth'] = auth;
				}
			} catch (err) {
				// If auth loading fails, proceed without auth
			}
		}

		return params;
	},

	/**
	 * Execute a Docker API action with consistent error handling and user feedback
	 * Automatically adds X-Registry-Auth header for push/pull operations if credentials exist
	 * Uses streaming for pull/push operations via onChunk callback
	 * @param {Function} apiMethod - The Docker API method to call
	 * @param {Object} params - Parameters to pass to the API method
	 * @param {string} actionName - Display name for the action
	 * @param {Object} [options={}] - Options for handleDockerResponse
	 * @returns {Promise<boolean>} - Promise that resolves to true/false based on success
	 */
	async executeDockerAction(apiMethod, params, actionName, options = {}) {
		try {
			params = await this.getRegistryAuth(params, actionName);

			// Detect if this is a streaming operation and add callback if needed
			const isPull = params?.query?.fromImage;
			const isPush = params?.name;
			const useStreaming = (isPull || isPush) && options.showOutput !== false;

			if (useStreaming) {
				params.onChunk = (chunk) => {
					const output = chunk.raw || JSON.stringify(chunk, null, 2);
					this.insertOutput(output + '\n');
				};
			}

			// Execute the API call
			const response = await apiMethod(params);
			return this.handleDockerResponse(response, actionName, options);

		} catch (err) {
			this.showNotification(
				actionName,
				err?.message || String(err) || _('Unexpected error'),
				options.errorDuration || 7000,
				'error'
			);
			if (options.onError) options.onError(err);
			return false;
		}
	},

	/**
	 * Flexible file/URI transfer with progress tracking and API preference
	 * @param {Object} options - Upload configuration
	 * @param {string} [options.method] - method to use: POST, PUT, etc
	 * @param {string} [options.commandCPath] - controller API endpoint path (e.g. '/images/load')
	 * @param {string} [options.commandDPath] - docker API endpoint path (e.g. '/images/load')
	 * @param {string} [options.commandTitle] - Title for the command modal
	 * @param {string} [options.commandMessage] - Message shown during command
	 * @param {string} [options.successMessage] - Message on successful command
	 * @param {string} [options.pathElementId] - Optional ID of element containing command path
	 * @param {string} [options.defaultPath='/'] - Default path if pathElementId is not provided
	 * @param {Function} [options.getFormData] - Optional function to customize FormData (receives file, path)
	 * @param {Function} [options.onUpdate] - Optional function to report status progress fed back
	 * @param {boolean} [options.noFileUpload] - If true, only a URI is uploaded (no file)
	 */
	async handleXHRTransfer(options = {}) {
		const {
			q_params = {},
			method = 'POST',
			commandCPath = null,
			commandDPath = null,
			commandTitle = null, //_('Uploading…'),
			commandMessage = null, //_('Uploading file…'),
			successMessage = _('Successful'),
			showProgress = true,
			pathElementId = null,
			defaultPath = '/',
			getFormData = null,
			onUpdate = null,
			noFileUpload = false,
		} = options;

		const view = this;
		let commandPath = defaultPath;
		let params = await this.getRegistryAuth(q_params, commandTitle);

		// Get path from element if specified
		if (pathElementId) {
			commandPath = document.getElementById(pathElementId)?.value || defaultPath;
			if (!commandPath || commandPath === '') {
				this.showNotification(_('Error'), _('Please specify a path'), 5000, 'error');
				return;
			}
		}

		// Build query string if params provided
		let query_str = '';
		if (params.query) {
			let parts = [];
			for (let [key, value] of Object.entries(params.query)) {
				if (key != null && value != '') {
					if (Array.isArray(value)) {
						value.map(e => parts.push(`${key}=${e}`));
						continue;
					}
					parts.push(`${key}=${value}`);
				}
			}
			if (parts.length)
				query_str = '?' + parts.join('&');
		}

		// Prefer JS API if available, else fallback to controller
		let destUrl = `${this.dockerman_url}${commandCPath}${query_str}`;
		let useRawFile = false;
		try {
			const [ok, host] = await apiReady;
			if (ok && host) {
				destUrl = host + commandDPath + query_str;
				useRawFile = true;
			}
		} catch { }

		// Show progress dialog with progress bar element
		let progressBar = E('div', { 
			'style': 'width:0%; background-color: #0066cc; height: 20px; border-radius: 3px; transition: width 0.3s ease;' 
		});
		let msgTxt = E('p', {}, commandMessage);
		let msgTitle = E('h4', {}, commandTitle);
		let progressText = E('p', {}, '0%');

		if (showProgress) {
			ui.showModal(msgTitle, [
				msgTxt,
				progressText,
				E('div', { 
					'class': 'cbi-progressbar', 
					'style': 'margin: 10px 0; background-color: #e0e0e0; border-radius: 3px; overflow: hidden;' 
				}, progressBar)
			]);
		}

		const xhr = new XMLHttpRequest();
		xhr.timeout = 0;

		// Track upload progress
		xhr.upload.addEventListener('progress', (e) => {
			if (e.lengthComputable) {
				const percentComplete = Math.round((e.loaded / e.total) * 100);
				progressBar.style.width = percentComplete + '%';
				progressText.textContent = percentComplete + '%';
			}
		});

		// Track progressive response progress
		let lastIndex = 0;
		// let title = _('Progress');
		xhr.onprogress = (upd) => {
			const chunk = xhr.responseText.slice(lastIndex);
			lastIndex = xhr.responseText.length;
			const lines = chunk.split('\n').filter(Boolean);
			for (const line of lines) {
				try {
					const msg = JSON.parse(line);
					const percentComplete = Math.round((msg?.progressDetail?.current / msg?.progressDetail?.total) * 100) || 0;
					if (msg.stream && msg.stream != '\n')
						msgTxt.innerHTML = ansiToHtml(msg?.stream);
					if (msg.status)
						msgTitle.innerHTML = msg?.status
					progressBar.style.width = percentComplete + '%';
					progressText.textContent = percentComplete + '%';
					if (onUpdate) onUpdate(msg);
				} catch (e) {}
			}
		};

		xhr.addEventListener('load', () => {
			ui.hideModal();
			if (xhr.status >= 200 && xhr.status < 300) {
				view.showNotification(
					_('Command successful'),
					successMessage,
					4000,
					'success'
				);
			} else {
				let errorMsg = xhr.responseText || `HTTP ${xhr.status}`;
				try {
					const json = JSON.parse(xhr.responseText);
					errorMsg = json.error || errorMsg;
				} catch (e) {}
				view.showNotification(
					_('Command failed'),
					errorMsg,
					7000,
					'error'
				);
			}
		});

		xhr.addEventListener('error', () => {
			ui.hideModal();
			view.showNotification(
				_('Command failed'),
				_('Network error'),
				7000,
				'error'
			);
		});

		xhr.addEventListener('abort', () => {
			ui.hideModal();
			view.showNotification(
				_('Command cancelled'),
				'',
				5000,
				'warning'
			);
		});

		if (noFileUpload) {
			this.handleURLOnlyForm(xhr, method, params, destUrl);
		} else {
			this.handleFileUploadForm(xhr, method, getFormData, destUrl, commandPath, useRawFile);
		}
	},


	handleURLOnlyForm(xhr, method, params, destUrl) {
		const formData = new FormData();
		formData.append('token', L.env.token);
		// if (params.name)
		// 	formData.append('name', params.name);

		xhr.open(method, destUrl);
		xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
		if (params.headers)
			for (let [hdr_name, hdr_value] of Object.entries(params.headers)) {
				xhr.setRequestHeader(hdr_name, hdr_value);
				// smuggle in the X-Registry-Auth header in the form data
				formData.append(hdr_name, hdr_value);
			}
		destUrl.includes(L.env.scriptname) ? xhr.send(formData) : xhr.send();
	},


	handleFileUploadForm(xhr, method, getFormData, destUrl, commandPath, useRawFile) {
		const fileInput = document.createElement('input');
		fileInput.type = 'file';
		fileInput.style.display = 'none';

		fileInput.onchange = (ev) => {
			const files = ev.target?.files;
			if (!files || files.length === 0) {
				ui.hideModal();
				return;
			}
			const file = files[0];

			// Create FormData with file
			let formData;
			if (getFormData) {
				formData = getFormData(file, commandPath);
			} else {
				formData = new FormData();
				/* 'token' is necessary when "post": true is defined for image load endpoint */
				formData.append('token', L.env.token);
				formData.append('upload-name', file.name);
				formData.append('upload-archive', file);
			}

			xhr.open(method, destUrl);
			xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
			
			if (useRawFile) {
				xhr.setRequestHeader('Content-Type', 'application/x-tar');
				xhr.send(file);
			} else {
				xhr.send(formData);
			}
		};

		fileInput.oncancel = (ev) => {
			ui.hideModal();
			return;
		}

		// Trigger file picker
		document.body.appendChild(fileInput);
		fileInput.click();
		document.body.removeChild(fileInput);
	},
});

// ANSI color code converter to HTML
const ansiToHtml = function(text) {
	if (!text) return '';

	// First, strip out terminal control sequences that aren't color codes
	// These include cursor positioning, screen clearing, etc.
	text = text
		// Strip CSI sequences (cursor movement, screen clearing, etc.)
		// eslint-disable-next-line no-control-regex
		.replace(/\x1B\[[0-9;?]*[A-Za-z]/g, (match) => {
			// Keep only SGR (Select Graphic Rendition) sequences ending in 'm'
			if (match.endsWith('m')) {
				return match;
			}
			// Strip everything else (cursor positioning, screen clearing, etc.)
			return '';
		})
		// Strip OSC sequences (window title, etc.)
		// eslint-disable-next-line no-control-regex
		.replace(/\x1B\][^\x07]*\x07/g, '')
		// Strip other escape sequences
		// eslint-disable-next-line no-control-regex
		.replace(/\x1B[><=]/g, '')
		// Strip bell character
		// eslint-disable-next-line no-control-regex
		.replace(/\x07/g, '');

	// ANSI color codes mapping
	const ansiColorMap = {
		'30': '#000000', // Black
		'31': '#FF5555', // Red
		'32': '#55FF55', // Green
		'33': '#FFFF55', // Yellow
		'34': '#5555FF', // Blue
		'35': '#FF55FF', // Magenta
		'36': '#55FFFF', // Cyan
		'37': '#FFFFFF', // White
		'90': '#555555', // Bright Black
		'91': '#FF8787', // Bright Red
		'92': '#87FF87', // Bright Green
		'93': '#FFFF87', // Bright Yellow
		'94': '#8787FF', // Bright Blue
		'95': '#FF87FF', // Bright Magenta
		'96': '#87FFFF', // Bright Cyan
		'97': '#FFFFFF', // Bright White
	};

	// Escape HTML special characters
	const escapeHtml = (str) => {
		const map = {
			'&': '&amp;',
			'<': '&lt;',
			'>': '&gt;',
			'"': '&quot;',
			"'": '&#039;'
		};
		return str.replace(/[&<>"']/g, m => map[m]);
	};

	// Split by ANSI escape sequences and process
	// eslint-disable-next-line no-control-regex
	const ansiRegex = /\x1B\[([\d;]*)m/g;
	let html = '';
	let currentStyle = {};
	let lastIndex = 0;
	let match;
	let textBuffer = '';

	// Helper to flush current text with current style
	const flushText = () => {
		if (textBuffer) {
			const escaped = escapeHtml(textBuffer);
			if (Object.keys(currentStyle).length > 0) {
				let styleStr = '';
				if (currentStyle.color) {
					styleStr += `color: ${currentStyle.color};`;
				}
				if (currentStyle.bgColor) {
					styleStr += `background-color: ${currentStyle.bgColor};`;
				}
				if (currentStyle.bold) {
					styleStr += 'font-weight: bold;';
				}
				if (currentStyle.italic) {
					styleStr += 'font-style: italic;';
				}
				if (currentStyle.underline) {
					styleStr += 'text-decoration: underline;';
				}
				if (styleStr) {
					html += `<span style="${styleStr}">${escaped}</span>`;
				} else {
					html += escaped;
				}
			} else {
				html += escaped;
			}
			textBuffer = '';
		}
	};

	while ((match = ansiRegex.exec(text)) !== null) {
		// Add text before this escape sequence
		if (match.index > lastIndex) {
			textBuffer += text.substring(lastIndex, match.index);
		}

		// Flush current text with old style before changing style
		flushText();

		const codes = match[1] ? match[1].split(';').map(Number) : [0];

		for (const code of codes) {
			if (code === 0) {
				// Reset all styles
				currentStyle = {};
			} else if (code === 1) {
				// Bold
				currentStyle.bold = true;
			} else if (code === 3) {
				// Italic
				currentStyle.italic = true;
			} else if (code === 4) {
				// Underline
				currentStyle.underline = true;
			} else if (code >= 30 && code <= 37) {
				// Standard foreground color
				currentStyle.color = ansiColorMap[code];
			} else if (code >= 90 && code <= 97) {
				// Bright foreground color
				currentStyle.color = ansiColorMap[code];
			} else if (code >= 40 && code <= 47) {
				// Background color
				currentStyle.bgColor = ansiColorMap[code - 10];
			}
		}

		lastIndex = match.index + match[0].length;
	}

	// Add any remaining text
	if (lastIndex < text.length) {
		textBuffer += text.substring(lastIndex);
	}
	flushText();

	// Convert newlines and carriage returns to <br/>
	html = html.replace(/\r\n/g, '<br/>').replace(/\r/g, '<br/>').replace(/\n/g, '<br/>');

	return html;
};

// Decide at call time whether to use JS API or RPC. Keep constructor synchronous.
let js_api_available = false;

// Store the JS API availability state
const apiReady = jsapi.js_api_available().then(([ok, host]) => {
	js_api_available = ok;
	return [ok, host];
}).catch(() => {
	js_api_available = false;
	return [false, null];	
});

const preferApi = (apiMethod, rpcMethod) => (...args) => {
	return apiReady.then(([ok, host]) => ok ? apiMethod(...args) : rpcMethod(...args));
};

return L.Class.extend({
	Types: Types,
	ActionTypes: ActionTypes,
	ansiToHtml: ansiToHtml,
	callMountPoints: callMountPoints,
	callRcInit: callRcInit,
	dv: dv,
	js_api_ready: apiReady,
	container_attach_ws: preferApi(jsapi.container_attach_ws, () => Promise.reject(new Error('Docker JS API not available'))),
	container_changes: preferApi(jsapi.container_changes, container_changes),
	container_create: preferApi(jsapi.container_create, container_create),
	// container_export: container_export, // use controller instead
	container_info_archive: preferApi(jsapi.container_info_archive, container_info_archive),
	container_inspect: preferApi(jsapi.container_inspect, container_inspect),
	container_kill: preferApi(jsapi.container_kill, container_kill),
	container_list: preferApi(jsapi.container_list, container_list),
	container_logs: preferApi(jsapi.container_logs, container_logs),
	container_pause: preferApi(jsapi.container_pause, container_pause),
	container_prune: preferApi(jsapi.container_prune, container_prune),
	container_remove: preferApi(jsapi.container_remove, container_remove),
	container_rename: preferApi(jsapi.container_rename, container_rename),
	container_restart: preferApi(jsapi.container_restart, container_restart),
	container_start: preferApi(jsapi.container_start, container_start),
	container_stats: preferApi(jsapi.container_stats, container_stats),
	container_stop: preferApi(jsapi.container_stop, container_stop),
	container_top: preferApi(jsapi.container_top, container_top),
	container_ttyd_start: container_ttyd_start,
	container_unpause: preferApi(jsapi.container_unpause, container_unpause),
	container_update: preferApi(jsapi.container_update, container_update),
	docker_df: preferApi(jsapi.docker_df, docker_df),
	docker_events: preferApi(jsapi.docker_events, docker_events),
	docker_info: preferApi(jsapi.docker_info, docker_info),
	docker_version: preferApi(jsapi.docker_version, docker_version),
	image_build: preferApi(jsapi.image_build, () => Promise.reject(new Error('Docker JS API not available'))),
	image_create: preferApi(jsapi.image_create, image_create),
	// image_get: image_get, // use controller instead
	image_history: preferApi(jsapi.image_history, image_history),
	image_inspect: preferApi(jsapi.image_inspect, image_inspect),
	image_list: preferApi(jsapi.image_list, image_list),
	image_prune: preferApi(jsapi.image_prune, image_prune),
	image_push: preferApi(jsapi.image_push, image_push),
	image_remove: preferApi(jsapi.image_remove, image_remove),
	image_tag: preferApi(jsapi.image_tag, image_tag),
	network_connect: preferApi(jsapi.network_connect, network_connect),
	network_create: preferApi(jsapi.network_create, network_create),
	network_disconnect: preferApi(jsapi.network_disconnect, network_disconnect),
	network_inspect: preferApi(jsapi.network_inspect, network_inspect),
	network_list: preferApi(jsapi.network_list, network_list),
	network_prune: preferApi(jsapi.network_prune, network_prune),
	network_remove: preferApi(jsapi.network_remove, network_remove),
	volume_create: preferApi(jsapi.volume_create, volume_create),
	volume_inspect: preferApi(jsapi.volume_inspect, volume_inspect),
	volume_list: preferApi(jsapi.volume_list, volume_list),
	volume_prune: preferApi(jsapi.volume_prune, volume_prune),
	volume_remove: preferApi(jsapi.volume_remove, volume_remove),
});

```

---

# configuration.js
```javascript
'use strict';
'require form';
'require fs';
'require tools.widgets as widgets';

/* 
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/


return L.view.extend({
	render() {
		const m = new form.Map('dockerd', _('Docker - Configuration'),
			_('DockerMan is a simple docker manager client for LuCI'));

		let o, t, s, ss;

		s = m.section(form.NamedSection, 'globals', 'section', _('Global settings'));

		t = s.tab('globals', _('Globals'));

		o = s.taboption('globals', form.Value, 'ps_flags',
			_('Default ps flags'),
			_('Flags passed to docker top (ps). Leave empty to use the built-in default.'));
		o.placeholder = '-ww';
		o.rmempty = true;
		o.optional = true;

		o = s.taboption('globals', form.Value, 'api_version',
			_('Api Version'),
			_('Lock API endpoint to a specific version (helps guarantee behaviour).') + '<br/>' +
			_('Causes errors when a chosen API > Docker endpoint API support.'));
		o.rmempty = true;
		o.optional = true;
		o.value('v1.44');
		o.value('v1.45');
		o.value('v1.46');
		o.value('v1.47');
		o.value('v1.48');
		o.value('v1.49');
		o.value('v1.50');
		o.value('v1.51');
		o.value('v1.52');

		// Check if local dockerd is available
		o = s.taboption('globals', form.DirectoryPicker, 'data_root', _('Docker Root Dir'),
			_('For local dockerd socket instances only.'));
		o.datatype = 'folder';
		o.default = '/opt/docker';
		o.root_directory = '/';
		o.show_hidden = true;

		o = s.taboption('globals', form.Value, 'bip',
			_('Default bridge'),
			_('Configure the default bridge network'));
		o.placeholder = '172.17.0.1/16';
		o.datatype = 'ipaddr';

		o = s.taboption('globals', form.DynamicList, 'registry_mirrors',
			_('Registry Mirrors'),
			_('It replaces the daemon registry mirrors with a new set of registry mirrors'));
		o.placeholder = _('Example: ') + 'https://hub-mirror.c.163.com';
		o.value('https://docker.io');
		o.value('https://ghcr.io');
		o.value('https://hub-mirror.c.163.com');

		o = s.taboption('globals', form.ListValue, 'log_level',
			_('Log Level'),
			_('Set the logging level'));
		o.value('debug', _('Debug'));
		o.value('', _('Info')); // default
		o.value('warn', _('Warning'));
		o.value('error', _('Error'));
		o.value('fatal', _('Fatal'));
		o.rmempty = true;

		o = s.taboption('globals', form.DynamicList, 'hosts',
			_('Client connection'),
			_('Specifies where the Docker daemon will listen for client connections. default: ') + 'unix:///var/run/docker.sock' + '<br />' + 
			_('Note that dockerd no longer listens on IP:port without TLS options after v27.'));
		o.placeholder = _('Example: tcp://0.0.0.0:2375');
		o.default = 'unix:///var/run/docker.sock';
		o.rmempty = true;
		o.value('unix:///var/run/docker.sock');
		o.value('tcp://0.0.0.0:2375');
		o.value('tcp://0.0.0.0:2376');
		o.value('tcp6://[::]:2375');
		o.value('tcp6://[::]:2376');

		o = s.taboption('globals', widgets.NetworkSelect, '_luci_lan',
			_('LAN connection'),
			_('Set your LAN interface when docker listens on all addresses like 0.0.0.0 or ::.'));
		o.rmempty = true;
		o.noaliases = true;
		o.nocreate = true;

		t = s.tab('auth', _('Registry Auth'));

		o = s.taboption('auth', form.SectionValue, '__auth__', form.TableSection, 'auth', null, 
			_('Used for push/pull operations on custom registries.') + '<br/>' +
			_('Destinations prefixed with a Registry host matching an entry in this table invoke its corresponding credentials.') + '<br/>' +
			_('The first match is used.') + '<br/>' +
			_('A Token is preferred over a Password.') + '<br/>' +
			_('Tokes and Passwords are not encrypted in the uci configuration.'));
		ss = o.subsection;
		ss.anonymous = true;
		ss.nodescriptions = true;
		ss.addremove = true;
		ss.sortable = true;

		o = ss.option(form.Value, 'username',
			_('User'));
		o.placeholder = 'jbloggs';
		o.rmempty = false;

		o = ss.option(form.Value, 'password',
			_('Password'));
		o.placeholder = 'foobar';
		o.password = true;

		o = ss.option(form.Value, 'serveraddress',
			_('Registry'));
		o.datatype = 'or(hostname,hostport,ipaddr,ipaddrport)';
		o.placeholder = 'registry.foo.io[:443] | 192.0.2.1[:443]';
		o.rmempty = false;
		o.value('container-registry.oracle.com');
		o.value('registry.docker.io');
		o.value('gcr.io');
		o.value('ghcr.io');
		o.value('quay.io');
		o.value('registry.gitlab.com');
		o.value('registry.redhat.io');

		o = ss.option(form.Value, 'token',
			_('Token'));
		o.password = true;


		return m.render();
	}
});

```

---

# container.js
```javascript
'use strict';
'require form';
'require fs';
'require poll';
'require uci';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/

const dummy_stats = {"read":"2026-01-08T22:57:31.547920715Z","pids_stats":{"current":3},"networks":{"eth0":{"rx_bytes":5338,"rx_dropped":0,"rx_errors":0,"rx_packets":36,"tx_bytes":648,"tx_dropped":0,"tx_errors":0,"tx_packets":8},"eth5":{"rx_bytes":4641,"rx_dropped":0,"rx_errors":0,"rx_packets":26,"tx_bytes":690,"tx_dropped":0,"tx_errors":0,"tx_packets":9}},"memory_stats":{"stats":{"total_pgmajfault":0,"cache":0,"mapped_file":0,"total_inactive_file":0,"pgpgout":414,"rss":6537216,"total_mapped_file":0,"writeback":0,"unevictable":0,"pgpgin":477,"total_unevictable":0,"pgmajfault":0,"total_rss":6537216,"total_rss_huge":6291456,"total_writeback":0,"total_inactive_anon":0,"rss_huge":6291456,"hierarchical_memory_limit":67108864,"total_pgfault":964,"total_active_file":0,"active_anon":6537216,"total_active_anon":6537216,"total_pgpgout":414,"total_cache":0,"inactive_anon":0,"active_file":0,"pgfault":964,"inactive_file":0,"total_pgpgin":477},"max_usage":6651904,"usage":6537216,"failcnt":0,"limit":67108864},"blkio_stats":{},"cpu_stats":{"cpu_usage":{"percpu_usage":[8646879,24472255,36438778,30657443],"usage_in_usermode":50000000,"total_usage":100215355,"usage_in_kernelmode":30000000},"system_cpu_usage":739306590000000,"online_cpus":4,"throttling_data":{"periods":0,"throttled_periods":0,"throttled_time":0}},"precpu_stats":{"cpu_usage":{"percpu_usage":[8646879,24350896,36438778,30657443],"usage_in_usermode":50000000,"total_usage":100093996,"usage_in_kernelmode":30000000},"system_cpu_usage":9492140000000,"online_cpus":4,"throttling_data":{"periods":0,"throttled_periods":0,"throttled_time":0}}};
const dummy_ps = {"Titles":["UID","PID","PPID","C","STIME","TTY","TIME","CMD"],"Processes":[["root","13642","882","0","17:03","pts/0","00:00:00","/bin/bash"],["root","13735","13642","0","17:06","pts/0","00:00:00","sleep 10"]]};
const dummy_changes = [{"Path":"/dev","Kind":0},{"Path":"/dev/kmsg","Kind":1},{"Path":"/test","Kind":1}];

// https://docs.docker.com/reference/api/engine/version/v1.47/#tag/Container/operation/ContainerStats
// Helper function to calculate memory usage percentage
function calculateMemoryUsage(stats) {
	if (!stats || !stats.memory_stats) return null;
	const mem = stats.memory_stats;
	if (!mem.usage || !mem.limit) return null;

	// used_memory = memory_stats.usage - memory_stats.stats.cache
	const cache = mem.stats?.cache || 0;
	const used_memory = mem.usage - cache;
	const available_memory = mem.limit;

	// Memory usage % = (used_memory / available_memory) * 100.0
	const percentage = (used_memory / available_memory) * 100.0;

	return {
		percentage: percentage,
		used: used_memory,
		limit: available_memory
	};
}

// Helper function to calculate CPU usage percentage
// Pass previousStats if Docker API doesn't provide complete precpu_stats
function calculateCPUUsage(stats, previousStats) {
	if (!stats || !stats.cpu_stats) return null;
	const cpu = stats.cpu_stats;

	// Try to use precpu_stats from API first, fall back to our stored previous stats
	let precpu = stats.precpu_stats;

	// If precpu_stats is incomplete, use our manually stored previous stats
	if (!precpu || !precpu.system_cpu_usage) {
		if (previousStats && previousStats.cpu_stats) {
			// console.log('Using manually stored previous CPU stats');
			precpu = previousStats.cpu_stats;
		} else {
			// console.log('No previous CPU stats available yet - waiting for next cycle');
			return null;
		}
	}

	// If we don't have both cpu_stats and precpu_stats, return null
	if (!cpu.cpu_usage || !precpu || !precpu.cpu_usage) {
		// console.log('CPU stats incomplete:', { 
		// 	hasCpu: !!cpu.cpu_usage, 
		// 	hasPrecpu: !!precpu,
		// 	hasPrecpuUsage: !!(precpu && precpu.cpu_usage)
		// });
		return null;
	}

	// Validate we have the required fields
	const validationChecks = {
		'cpu.cpu_usage.total_usage': typeof cpu.cpu_usage.total_usage,
		'precpu.cpu_usage.total_usage': typeof precpu.cpu_usage.total_usage,
		'cpu.system_cpu_usage': typeof cpu.system_cpu_usage,
		'precpu.system_cpu_usage': typeof precpu.system_cpu_usage,
		'cpu_values': {
			cpu_total: cpu.cpu_usage.total_usage,
			precpu_total: precpu.cpu_usage.total_usage,
			cpu_system: cpu.system_cpu_usage,
			precpu_system: precpu.system_cpu_usage
		}
	};

	// Check if we have valid numeric values for all required fields
	// Note: precpu_stats may be empty/undefined on first stats call
	if (typeof cpu.cpu_usage.total_usage !== 'number' || 
		typeof precpu.cpu_usage.total_usage !== 'number' ||
		typeof cpu.system_cpu_usage !== 'number' ||
		typeof precpu.system_cpu_usage !== 'number') {
		// console.log('CPU stats incomplete - waiting for valid precpu data:', validationChecks);
		return null;
	}

	// Also check if precpu data is essentially zero (first call scenario)
	if (precpu.cpu_usage.total_usage === 0 || precpu.system_cpu_usage === 0) {
		// console.log('CPU precpu stats are zero - waiting for next stats cycle');
		return null;
	}

	// cpu_delta = cpu_stats.cpu_usage.total_usage - precpu_stats.cpu_usage.total_usage
	const cpu_delta = cpu.cpu_usage.total_usage - precpu.cpu_usage.total_usage;

	// system_cpu_delta = cpu_stats.system_cpu_usage - precpu_stats.system_cpu_usage
	const system_cpu_delta = cpu.system_cpu_usage - precpu.system_cpu_usage;

	// Validate deltas
	if (system_cpu_delta <= 0 || cpu_delta < 0) {
		// console.warn('Invalid CPU deltas:', { 
		// 	cpu_delta, 
		// 	system_cpu_delta,
		// 	cpu_total: cpu.cpu_usage.total_usage,
		// 	precpu_total: precpu.cpu_usage.total_usage,
		// 	system: cpu.system_cpu_usage,
		// 	presystem: precpu.system_cpu_usage
		// });
		return null;
	}

	// number_cpus = length(cpu_stats.cpu_usage.percpu_usage) or cpu_stats.online_cpus
	const number_cpus = cpu.online_cpus || (cpu.cpu_usage.percpu_usage?.length || 1);

	// CPU usage % = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
	const percentage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0;

	// console.log('CPU calculation:', { 
	// 	cpu_delta, 
	// 	system_cpu_delta, 
	// 	number_cpus, 
	// 	percentage: percentage.toFixed(2) + '%'
	// });

	return {
		percentage: percentage,
		number_cpus: number_cpus
	};
}

// Helper function to create a progress bar
function createProgressBar(label, percentage, used, total) {
	const clampedPercentage = Math.min(Math.max(percentage || 0, 0), 100);
	const color = clampedPercentage > 90 ? '#d9534f' : (clampedPercentage > 70 ? '#f0ad4e' : '#5cb85c');

	return E('div', { 'style': 'margin: 10px 0;' }, [
		E('div', { 'style': 'display: flex; justify-content: space-between; margin-bottom: 5px;' }, [
			E('span', { 'style': 'font-weight: bold;' }, label),
			E('span', {}, used && total ? `${used} / ${total}` : `${clampedPercentage.toFixed(2)}%`)
		]),
		E('div', { 
			'style': 'width: 100%; height: 20px; background-color: #e9ecef; border-radius: 4px; overflow: hidden;'
		}, [
			E('div', {
				'style': `width: ${clampedPercentage}%; height: 100%; background-color: ${color}; transition: width 0.3s ease;`
			})
		])
	]);
}


const ChangeTypes = Object.freeze({
	0: 'Modified',
	1: 'Added',
	2: 'Deleted',
});

return dm2.dv.extend({
	load() {
		const requestPath = L.env.requestpath;
		const containerId = requestPath[requestPath.length-1] || '';
		this.psArgs = uci.get('dockerd', 'globals', 'ps_flags') || '-ww';

		// First load container info to check state
		return dm2.container_inspect({id: containerId})
			.then(container => {
				if (container.code !== 200) window.location.href = `${this.dockerman_url}/containers`;
				const this_container = container.body || {};

				// Now load other resources, conditionally calling stats/ps/changes only if running
				const isRunning = this_container.State?.Status === 'running';

				return Promise.all([
					this_container,
					dm2.image_list().then(images => {
						return Array.isArray(images.body) ? images.body : [];
					}),
					dm2.network_list().then(networks => {
						return Array.isArray(networks.body) ? networks.body : [];
					}),
					dm2.docker_info().then(info => {
						const numcpus = info.body?.NCPU || 1.0;
						const memory = info.body?.MemTotal || 2**10;
						return {numcpus: numcpus, memory: memory};
					}),
					isRunning ? dm2.container_top({ id: containerId, query: { 'ps_args': this.psArgs || '-ww' } })
						.then(res => {
							if (res?.code < 300 && res.body) return res.body;
							else return dummy_ps;
						})
						.catch(() => {}) : Promise.resolve(),
					isRunning ? dm2.container_stats({ id: containerId, query: { 'stream': false, 'one-shot': true } })
						.then(res => {
							if (res?.code < 300 && res.body) return res.body;
							else return dummy_stats;
						})
						.catch(() => {}) : Promise.resolve(),
					dm2.container_changes({ id: containerId })
						.then(res => {
							if (res?.code < 300 && Array.isArray(res.body)) return res.body;
							else return dummy_changes;
						})
						.catch(() => {}),
				]);
			});
	},

	buildList(array, mapper) {
		if (!Array.isArray(array)) return [];
		const out = [];
		for (const item of array) {
			const mapped = mapper(item);
			if (mapped || mapped === 0)
				out.push(mapped);
		}
		return out;
	},

	buildListFromObject(obj, mapper) {
		if (!obj || typeof obj !== 'object') return [];
		const out = [];
		for (const [k, v] of Object.entries(obj)) {
			const mapped = mapper(k, v);
			if (mapped || mapped === 0)
				out.push(mapped);
		}
		return out;
	},

	getMountsList(this_container) {
		return this.buildList(this_container?.Mounts, (mount) => {
			if (!mount?.Type || !mount?.Destination) return null;
			let entry = `${mount.Type}:${mount.Source}:${mount.Destination}`;
			if (mount.Mode) entry += `:${mount.Mode}`;
			return entry;
		});
	},

	getPortsList(this_container) {
		const portBindings = this_container?.HostConfig?.PortBindings;
		if (!portBindings || typeof portBindings !== 'object') return [];
		const ports = [];
		for (const [containerPort, bindings] of Object.entries(portBindings)) {
			if (Array.isArray(bindings) && bindings.length > 0 && bindings[0]?.HostPort) {
				ports.push(`${bindings[0].HostPort}:${containerPort}`);
			}
		}
		return ports;
	},

	getEnvList(this_container) {
		return this_container?.Config?.Env || [];
	},

	getDevicesList(this_container) {
		return this.buildList(this_container?.HostConfig?.Devices, (device) => {
			if (!device?.PathOnHost || !device?.PathInContainer) return null;
			let entry = `${device.PathOnHost}:${device.PathInContainer}`;
			if (device.CgroupPermissions) entry += `:${device.CgroupPermissions}`;
			return entry;
		});
	},

	getTmpfsList(this_container) {
		return this.buildListFromObject(this_container?.HostConfig?.Tmpfs, (path, opts) => `${path}${opts ? ':' + opts : ''}`);
	},

	getDnsList(this_container) {
		return this_container?.HostConfig?.Dns || [];
	},

	getSysctlList(this_container) {
		return this.buildListFromObject(this_container?.HostConfig?.Sysctls, (key, value) => `${key}:${value}`);
	},

	getCapAddList(this_container) {
		return this_container?.HostConfig?.CapAdd || [];
	},

	getLogOptList(this_container) {
		return this.buildListFromObject(this_container?.HostConfig?.LogConfig?.Config, (key, value) => `${key}=${value}`);
	},

	getCNetworksArray(c_networks, networks) {
		if (!c_networks || typeof c_networks !== 'object') return [];
		const data = [];

		for (const [name, net] of Object.entries(c_networks)) {
			const network = networks.find(n => n.Name === name || n.Id === name);
			const netid = !net?.NetworkID ? network?.Id : net?.NetworkID;

			/* Even if netid is null, proceed: perhaps the network was deleted. If we
			display it, the user can disconnect it. */
			data.push({
				...net,
				_shortId: netid?.substring(0,12) ||  '',
				Name: name,
				NetworkID: netid,
				DNSNames: net?.DNSNames || '',
				IPv4Address: net?.IPAMConfig?.IPv4Address || '',
				IPv6Address: net?.IPAMConfig?.IPv6Address || '',
			});
		}

		return data;
	},

	render([this_container, images, networks, cpus_mem, ps_top, stats_data, changes_data]) {
		const view = this;
		const containerName = this_container.Name?.substring(1) || this_container.Id || '';
		const containerIdShort = (this_container.Id || '').substring(0, 12);
		const c_networks = this_container.NetworkSettings?.Networks || {};

		// Create main container with action buttons
		const mainContainer = E('div', {});

		const containerStatus = this.getContainerStatus(this_container);

		// Add title and description
		const header = E('div', { 'class': 'cbi-page' }, [
			E('h2', {}, _('Docker - Container')),
			E('p', { 'style': 'margin: 10px 0; display: flex; gap: 6px; align-items: center;' }, [
				this.wrapStatusText(containerName, containerStatus, 'font-weight:600;'),
				E('span', { 'style': 'color:#666;' }, `(${containerIdShort})`)
			]),
			E('p', { 'style': 'color: #666;' }, _('Manage and view container configuration'))
		]);
		mainContainer.appendChild(header);

		// Add action buttons section
		const buttonSection = E('div', { 'class': 'cbi-section', 'style': 'margin-bottom: 20px;' });
		const buttonContainer = E('div', { 'style': 'display: flex; gap: 10px; flex-wrap: wrap;' });

		// Start button
		if (containerStatus !== 'running') {
			const startBtn = E('button', {
				'class': 'cbi-button cbi-button-apply',
				'click': (ev) => this.executeAction(ev, 'start', this_container.Id)
			}, [_('Start')]);
			buttonContainer.appendChild(startBtn);
		}

		// Restart button
		if (containerStatus === 'running') {
			const restartBtn = E('button', {
				'class': 'cbi-button cbi-button-reload',
				'click': (ev) => this.executeAction(ev, 'restart', this_container.Id)
			}, [_('Restart')]);
			buttonContainer.appendChild(restartBtn);
		}

		// Stop button
		if (containerStatus === 'running' || containerStatus === 'paused') {
			const stopBtn = E('button', {
				'class': 'cbi-button cbi-button-reset',
				'click': (ev) => this.executeAction(ev, 'stop', this_container.Id)
			}, [_('Stop')]);
			buttonContainer.appendChild(stopBtn);
		}

		// Kill button
		if (containerStatus === 'running') {
			const killBtn = E('button', {
				'class': 'cbi-button',
				'style': 'background-color: #dc3545;',
				'click': (ev) => this.executeAction(ev, 'kill', this_container.Id)
			}, [_('Kill')]);
			buttonContainer.appendChild(killBtn);
		}

		// Pause/Unpause button
		if (containerStatus === 'running' || containerStatus === 'paused') {
			const isPausedNow = this.container?.State?.Paused === true;
			const pauseBtn = E('button', {
				'class': 'cbi-button',
				'id': 'pause-button',
				'click': (ev) => {
					const currentStatus = this.getContainerStatus(this_container);
					this.executeAction(ev, (currentStatus === 'paused' ? 'unpause' : 'pause'), this_container.Id);
				}
			}, [isPausedNow ? _('Unpause') : _('Pause')]);
			buttonContainer.appendChild(pauseBtn);
		}

		// Duplicate button
		const duplicateBtn = E('button', {
			'class': 'cbi-button cbi-button-add',
			'click': (ev) => {
				ev.preventDefault();
				window.location.href = `${this.dockerman_url}/container_new/duplicate/${this_container.Id}`;
			}
		}, [_('Duplicate/Edit')]);
		buttonContainer.appendChild(duplicateBtn);

		// Export button
		const exportBtn = E('button', {
			'class': 'cbi-button cbi-button-reload',
			'click': (ev) => {
				ev.preventDefault();
				window.location.href = `${this.dockerman_url}/container/export/${this_container.Id}`;
			}
		}, [_('Export')]);
		buttonContainer.appendChild(exportBtn);

		// Remove button
		const removeBtn = E('button', {
			'class': 'cbi-button cbi-button-remove',
			'click': (ev) => this.executeAction(ev, 'remove', this_container.Id),
		}, [_('Remove')]);
		buttonContainer.appendChild(removeBtn);

		// Back button
		const backBtn = E('button', {
			'class': 'cbi-button',
			'click': () => window.location.href = `${this.dockerman_url}/containers`,
		}, [_('Back to Containers')]);
		buttonContainer.appendChild(backBtn);

		buttonSection.appendChild(buttonContainer);
		mainContainer.appendChild(buttonSection);


		const m = new form.JSONMap({
			cont: this_container,
			nets: this.getCNetworksArray(c_networks, networks),
			hostcfg: this_container.HostConfig || {},
		}, null);
		m.submit = false;
		m.reset = false;

		let s = m.section(form.NamedSection, 'cont', null, _('Container detail'));
		s.anonymous = true;
		s.nodescriptions = true;
		s.addremove = false;

		let o, ss;

		s.tab('info', _('Info'));

		o = s.taboption('info', form.Value, 'Name', _('Name'));

		o = s.taboption('info', form.DummyValue, 'Id', _('ID'));

		o = s.taboption('info', form.DummyValue, 'Image', _('Image'));
		o.cfgvalue = (sid) => this.getImageFirstTag(images, this.map.data.data[sid].Image);

		o = s.taboption('info', form.DummyValue, 'Image', _('Image ID'));

		o = s.taboption('info', form.DummyValue, 'status', _('Status'));
		o.cfgvalue = (sid) => this.map.data.data[sid].State?.Status || '';

		o = s.taboption('info', form.DummyValue, 'Created', _('Created'));

		o = s.taboption('info', form.DummyValue, 'started', _('Finish Time'));
		o.cfgvalue = () => {
			if (this_container.State?.Running)
				return this_container.State?.StartedAt || '-';
			return this_container.State?.FinishedAt || '-';
		};

		o = s.taboption('info', form.DummyValue, 'healthy', _('Health Status'));
		o.cfgvalue = () => this_container.State?.Health?.Status || '-';

		o = s.taboption('info', form.DummyValue, 'user', _('User'));
		o.cfgvalue = () => this_container.Config?.User || '-';

		o = s.taboption('info', form.ListValue, 'restart_policy', _('Restart Policy'));
		o.cfgvalue = () => this_container.HostConfig?.RestartPolicy?.Name || '-';
		o.value('no', _('No'));
		o.value('unless-stopped', _('Unless stopped'));
		o.value('always', _('Always'));
		o.value('on-failure', _('On failure'));

		o = s.taboption('info', form.DummyValue, 'hostname', _('Host Name'));
		o.cfgvalue = () => this_container.Config?.Hostname || '-';

		o = s.taboption('info', form.DummyValue, 'command', _('Command'));
		o.cfgvalue = () => {
			const cmd = this_container.Config?.Cmd;
			if (Array.isArray(cmd))
				return cmd.join(' ');
			return cmd || '-';
		};

		o = s.taboption('info', form.DummyValue, 'env', _('Env'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const env = this.getEnvList(this_container);
			return env.length > 0 ? env.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'ports', _('Ports'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const ports = view.getPortsList(this_container);
			return ports.length > 0 ? ports.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'links', _('Links'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const links = this_container.HostConfig?.Links;
			return Array.isArray(links) && links.length > 0 ? links.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'devices', _('Devices'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const devices = this.getDevicesList(this_container);
			return devices.length > 0 ? devices.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'tmpfs', _('Tmpfs Directories'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const tmpfs = this.getTmpfsList(this_container);
			return tmpfs.length > 0 ? tmpfs.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'dns', _('DNS'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const dns = view.getDnsList(this_container);
			return dns.length > 0 ? dns.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'sysctl', _('Sysctl Settings'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const sysctl = this.getSysctlList(this_container);
			return sysctl.length > 0 ? sysctl.join('<br />') : '-';
		};

		o = s.taboption('info', form.DummyValue, 'mounts', _('Mounts/Binds'));
		o.rawhtml = true;
		o.cfgvalue = () => {
			const mounts = view.getMountsList(this_container);
			return mounts.length > 0 ? mounts.join('<br />') : '-';
		};

		// NETWORKS TAB
		s.tab('network', _('Networks'));

		o = s.taboption('network', form.SectionValue, '__net__', form.TableSection, 'nets', null);
		ss = o.subsection;
		ss.anonymous = true;
		ss.nodescriptions = true;
		ss.addremove = true;
		ss.addbtntitle = _('Connect') + ' 🔗';
		ss.delbtntitle = _('Disconnect') + ' ⛓️‍💥';

		o = ss.option(form.DummyValue, 'Name', _('Name'));

		o = ss.option(form.DummyValue, '_shortId', _('ID'));
		o.cfgvalue = function(section_id, value) {
			const name_links = false;
			const nets = this.map.data.data[section_id] || {};
			return view.parseNetworkLinksForContainer(networks, (Array.isArray(nets) ? nets : [nets]), name_links);
		};

		o = ss.option(form.DummyValue, 'IPv4Address', _('IPv4 Address'));

		o = ss.option(form.DummyValue, 'IPv6Address', _('IPv6 Address'));

		o = ss.option(form.DummyValue, 'GlobalIPv6Address', _('Global IPv6 Address'));

		o = ss.option(form.DummyValue, 'MacAddress', _('MAC Address'));

		o = ss.option(form.DummyValue, 'Gateway', _('Gateway'));

		o = ss.option(form.DummyValue, 'IPv6Gateway', _('IPv6 Gateway'));

		o = ss.option(form.DummyValue, 'DNSNames', _('DNS Names'));

		ss.handleAdd = function(ev) {
			ev.preventDefault();
			view.executeNetworkAction('connect', null, null, this_container);
		};

		ss.handleRemove = function(section_id, ev) {
			const network = this.map.data.data[section_id];
			ev.preventDefault();
			delete this.map.data.data[section_id];
			this.super('handleRemove', [ev]);
			view.executeNetworkAction('disconnect', (network.NetworkID || network.Name), network.Name, this_container);
		};



		s.tab('resources', _('Resources'));

		o = s.taboption('resources', form.SectionValue, '__hcfg__', form.TypedSection, 'hostcfg', null);
		ss = o.subsection;
		ss.anonymous = true;
		ss.nodescriptions = false;
		ss.addremove = false;

		o = ss.option(form.Value, 'NanoCpus', _('CPUs'));
		o.cfgvalue = (sid) => view.map.data.data[sid].NanoCpus / (10**9);
		o.placeholder='1.5';
		o.datatype = 'ufloat';
		o.validate = function(section_id, value) {
			if (!value) return true;
			if (value > cpus_mem.numcpus) return _(`Only ${cpus_mem.numcpus} CPUs available`);
			return true;
		};

		o = ss.option(form.Value, 'CpuPeriod', _('CPU Period (microseconds)'));
		o.datatype = 'or(and(uinteger,min(1000),max(1000000)),"0")';

		o = ss.option(form.Value, 'CpuQuota', _('CPU Quota (microseconds)'));
		o.datatype = 'uinteger';

		o = ss.option(form.Value, 'CpuShares', _('CPU Shares Weight'));
		o.placeholder='1024';
		o.datatype = 'uinteger';

		o = ss.option(form.Value, 'Memory', _('Memory Limit'));
		o.cfgvalue = (sid, val) => {
			const mem = view.map.data.data[sid].Memory;
			return mem ? '%1024.2m'.format(mem) : 0;
		};
		o.write = function(sid, val) {
			if (!val || val == 0) return 0;
			this.map.data.data[sid].Memory = view.parseMemory(val);
			return view.parseMemory(val) || 0;
		};
		o.validate = function(sid, value) {
			if (!value) return true;
			if (value > view.memory) return _(`Only ${view.memory} bytes available`);
			return true;
		};

		o = ss.option(form.Value, 'MemorySwap', _('Memory + Swap'));
		o.cfgvalue = (sid, val) => {
			const swap = this.map.data.data[sid].MemorySwap;
			return swap ? '%1024.2m'.format(swap) : 0;
		};
		o.write = function(sid, val) {
			if (!val || val == 0) return 0;
			this.map.data.data[sid].MemorySwap = view.parseMemory(val);
			return view.parseMemory(val) || 0;
		};

		o = ss.option(form.Value, 'MemoryReservation', _('Memory Reservation'));
		o.cfgvalue = (sid, val) => {
			const res = this.map.data.data[sid].MemoryReservation;
			return res ? '%1024.2m'.format(res) : 0;
		};
		o.write = function(sid, val) {
			if (!val || val == 0) return 0;
			this.map.data.data[sid].MemoryReservation = view.parseMemory(val);
			return view.parseMemory(val) || 0;
		};

		o = ss.option(form.Flag, 'OomKillDisable', _('OOM Kill Disable'));

		o = ss.option(form.Value, 'BlkioWeight', _('Block IO Weight'));
		o.datatype = 'and(uinteger,min(0),max(1000)';

		o = ss.option(form.DummyValue, 'Privileged', _('Privileged Mode'));
		o.cfgvalue = (sid, val) => this.map.data.data[sid]?.Privileged ? _('Yes') : _('No');

		o = ss.option(form.DummyValue, 'CapAdd', _('Added Capabilities'));
		o.cfgvalue = (sid, val) => {
			const caps = this.map.data.data[sid]?.CapAdd;
			return Array.isArray(caps) && caps.length > 0 ? caps.join(', ') : '-';
		};

		o = ss.option(form.DummyValue, 'CapDrop', _('Dropped Capabilities'));
		o.cfgvalue = (sid, val) => {
			const caps = this.map.data.data[sid]?.CapDrop;
			return Array.isArray(caps) && caps.length > 0 ? caps.join(', ') : '-';
		};

		o = ss.option(form.DummyValue, 'LogDriver', _('Log Driver'));
		o.cfgvalue = (sid) => this.map.data.data[sid].LogConfig?.Type || '-';

		o = ss.option(form.DummyValue, 'log_opt', _('Log Options'));
		o.cfgvalue = () => {
			const opts = this.getLogOptList(this_container);
			return opts.length > 0 ? opts.join('<br />') : '-';
		};

		// STATS TAB
		s.tab('stats', _('Stats'));

		function updateStats(stats_data) {
			const status = view.getContainerStatus(this_container);

			if (status !== 'running') {
				// If we already have UI elements, clear/update them
				if (view.statsTable) {
					const progressBarsSection = document.getElementById('stats-progress-bars');
					if (progressBarsSection) {
						progressBarsSection.innerHTML = '';
						progressBarsSection.appendChild(E('p', {}, _('Container is not running') + ' (' + _('Status') + ': ' + status + ')'));
					}
					try { view.statsTable.update([]); } catch (e) {}
				}

				return E('div', { 'class': 'cbi-section' }, [
					E('p', {}, [
						_('Container is not running') + ' (' + _('Status') + ': ' + status + ')'
					])
				]);
			}

			const stats = stats_data || dummy_stats;

			// Calculate usage percentages
			const memUsage = calculateMemoryUsage(stats);
			const cpuUsage = calculateCPUUsage(stats, view.previousCpuStats);

			// Store current stats for next calculation
			view.previousCpuStats = stats;

			// Prepare rows
			const rows = [
				[_('PID Stats'), view.objectToText(stats.pids_stats)],
				[_('Net Stats'), view.objectToText(stats.networks)],
				[_('Mem Stats'), view.objectToText(stats.memory_stats)],
				[_('BlkIO Stats'), view.objectToText(stats.blkio_stats)],
				[_('CPU Stats'), view.objectToText(stats.cpu_stats)],
				[_('Per CPU Stats'), view.objectToText(stats.precpu_stats)]
			];

			// If table already exists (polling update), update in-place
			if (view.statsTable) {
				try {
					view.statsTable.update(rows);
				} catch (e) { console.error('Failed to update stats table', e); }

				// Update progress bars
				const progressBarsSection = document.getElementById('stats-progress-bars');
				if (progressBarsSection) {
					progressBarsSection.innerHTML = '';
					progressBarsSection.appendChild(E('h3', {}, _('Resource Usage')));
					progressBarsSection.appendChild(
						memUsage ? createProgressBar(
							_('Memory Usage'),
							memUsage.percentage,
							'%1024.2m'.format(memUsage.used),
							'%1024.2m'.format(memUsage.limit)
						) : E('div', {}, _('Memory usage data unavailable'))
					);
					progressBarsSection.appendChild(
						cpuUsage ? createProgressBar(
							_('CPU Usage') + ` (${cpuUsage.number_cpus} CPUs)`,
							cpuUsage.percentage,
							null,
							null
						) : E('div', {}, _('CPU usage data unavailable'))
					);
				}

				// Update raw JSON field
				const statsField = document.getElementById('raw-stats-field');
				if (statsField) statsField.textContent = JSON.stringify(stats, null, 2);

				return true;
			}

			// Create progress bars section (initial render)
			const progressBarsSection = E('div', { 
				'class': 'cbi-section',
				'id': 'stats-progress-bars',
				'style': 'margin-bottom: 20px;'
			}, [
				E('h3', {}, _('Resource Usage')),
				memUsage ? createProgressBar(
					_('Memory Usage'),
					memUsage.percentage,
					'%1024.2m'.format(memUsage.used),
					'%1024.2m'.format(memUsage.limit)
				) : E('div', {}, _('Memory usage data unavailable')),
				cpuUsage ? createProgressBar(
					_('CPU Usage') + ` (${cpuUsage.number_cpus} CPUs)`,
					cpuUsage.percentage,
					null,
					null
				) : E('div', {}, _('CPU usage data unavailable'))
			]);

			const statsTable = new L.ui.Table(
				[_('Metric'), _('Value')],
				{ id: 'stats-table' },
				E('em', [_('No statistics available')])
			);

			// Store table reference for poll updates
			view.statsTable = statsTable;

			// Initial data
			statsTable.update(rows);

			return E('div', { 'class': 'cbi-section' }, [
				progressBarsSection,
				statsTable.render(),
				E('h3', { 'style': 'margin-top: 20px;' }, _('Raw JSON')),
				E('pre', { 
					style: 'overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;', 
					id: 'raw-stats-field' 
				}, JSON.stringify(stats, null, 2))
			]);
		};

		// Create custom table for stats using L.ui.Table
		o = s.taboption('stats', form.DummyValue, '_stats_table', _('Container Statistics'));
		o.render = L.bind(() => { return updateStats(stats_data)}, this);

		// PROCESS TAB
		s.tab('ps', _('Processes'));

		// Create custom table for processes using L.ui.Table
		o = s.taboption('ps', form.DummyValue, '_ps_table', _('Running Processes'));
		o.render = L.bind(() => {
			const status = this.getContainerStatus(this_container);

			if (status !== 'running') {
				return E('div', { 'class': 'cbi-section' }, [
					E('p', {}, [
						_('Container is not running') + ' (' + _('Status') + ': ' + status + ')'
					])
				]);
			}

			// Use titles from the loaded data, or fallback to default
			const titles = (ps_top && ps_top.Titles) ? ps_top.Titles : 
				[_('PID'), _('USER'), _('VSZ'), _('STAT'), _('COMMAND')];

			// Store raw titles (without translation) for comparison in poll
			this.psTitles = titles;

			const psTable = new L.ui.Table(
				titles.map(t => _(t)),
				{ id: 'ps-table' },
				E('em', [_('No processes running')])
			);

			// Store table reference and titles for poll updates
			this.psTable = psTable;
			this.psTitles = titles;

			// Initial data from dummy_ps
			if (ps_top && ps_top.Processes) {
				psTable.update(ps_top.Processes);
			}

			return E('div', { 'class': 'cbi-section' }, [
				E('div', { 'style': 'margin-bottom: 10px;' }, [
					E('label', { 'for': 'ps-flags-input', 'style': 'margin-right: 8px;' }, _('ps flags:')),
					E('input', {
						id: 'ps-flags-input',
						'class': 'cbi-input-text',
						'type': 'text',
						'value': this.psArgs || '-ww',
						'placeholder': '-ww',
						'style': 'width: 200px;',
						'input': (ev) => { this.psArgs = ev.target.value || '-ww'; }
					})
				]),
				psTable.render(),
				E('h3', { 'style': 'margin-top: 20px;' }, _('Raw JSON')),
				E('pre', { 
					style: 'overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;', 
					id: 'raw-ps-field' 
				}, JSON.stringify(ps_top || dummy_ps, null, 2))
			]);
		}, this);

		// CHANGES TAB
		s.tab('changes', _('Changes'));

		// Create custom table for changes using L.ui.Table
		o = s.taboption('changes', form.DummyValue, '_changes_table', _('Filesystem Changes'));
		o.render = L.bind(() => {
			const changesTable = new L.ui.Table(
				[_('Kind'), _('Path')],
				{ id: 'changes-table' },
				E('em', [_('No filesystem changes detected')])
			);

			// Store table reference for poll updates
			this.changesTable = changesTable;

			// Initial data
			const rows = (changes_data || dummy_changes).map(change => [
				ChangeTypes[change?.Kind] || change?.Kind,
				change?.Path
			]);
			changesTable.update(rows);

			return E('div', { 'class': 'cbi-section' }, [
				changesTable.render(),
				E('h3', { 'style': 'margin-top: 20px;' }, _('Raw JSON')),
				E('pre', { 
					style: 'overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;', 
					id: 'raw-changes-field' 
				}, JSON.stringify(changes_data || dummy_changes, null, 2))
			]);
		}, this);



		// FILE TAB
		s.tab('file', _('File'));
		let fileDiv = null;

		o = s.taboption('file', form.DummyValue, 'json', '_file');
		o.cfgvalue = (sid, val) => '/';
		o.render = L.bind(() => {
			if (fileDiv) {
				return fileDiv;
			}

			fileDiv = E('div', { 'class': 'cbi-section' }, [
				E('div', { 'style': 'margin-bottom: 10px;' }, [
					E('label', { 'style': 'margin-right: 10px;' }, _('Path:')),
					E('input', {
						'type': 'text',
						'id': 'file-path',
						'class': 'cbi-input-text',
						'value': '/',
						'style': 'width: 200px;'
					}),
					E('button', {
						'class': 'cbi-button cbi-button-positive',
						'style': 'margin-left: 10px;',
						'click': () => this.handleFileUpload(this_container.Id),
					}, _('Upload') + ' ⬆️'),
					E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'style': 'margin-left: 5px;',
						'click': () => this.handleFileDownload(this_container.Id),
					}, _('Download') + ' ⬇️'),
					E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'style': 'margin-left: 5px;',
						'click': () => this.handleInfoArchive(this_container.Id),
					}, _('Inspect') + ' 🔎'),
				]),
				E('textarea', {
					'id': 'container-file-text',
					'readonly': true,
					'rows': '5',
					'style': 'width: 100%; font-family: monospace; font-size: 12px; padding: 10px; border: 1px solid #ccc;'
				}, '')
			]);

			return fileDiv;
		}, this);


		// INSPECT TAB
		s.tab('inspect', _('Inspect'));
		let inspectDiv = null;

		o = s.taboption('inspect', form.Button, 'json', _('Container Inspect'));
		o.render = L.bind(() => {
			if (inspectDiv) {
				return inspectDiv;
			}

			inspectDiv = E('div', { 'class': 'cbi-section' }, [
				E('div', { 'style': 'margin-bottom: 10px;' }, [
					E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'style': 'margin-left: 5px;',
						'click': () => dm2.container_inspect({ id: this_container.Id }).then(response => {
							const output = document.getElementById('container-inspect-output');
							output.textContent = JSON.stringify(response.body, null, 2);
							return;
						}),
					}, _('Inspect') + ' 🔎'),
				]),
			]);

			return inspectDiv;
		}, this);

		o = s.taboption('inspect', form.DummyValue, 'json');
		o.cfgvalue = () => E('pre', { style: 'overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;',
			id: 'container-inspect-output' }, 
			JSON.stringify(this_container, null, 2));


		// TERMINAL TAB
		s.tab('console', _('Console'));

		o = s.taboption('console', form.DummyValue, 'console_controls', _('Console Connection'));
		o.render = L.bind(() => {
			const status = this.getContainerStatus(this_container);
			const isRunning = status === 'running';

			if (!isRunning) {
				return E('div', { 'class': 'alert-message warning' },
					_('Container is not running. Cannot connect to console.'));
			}

			const consoleDiv = E('div', { 'class': 'cbi-section' }, [
				E('div', { 'style': 'margin-bottom: 15px;' }, [
					E('label', { 'style': 'margin-right: 10px;' }, _('Command:')),
					E('span', { 'id': 'console-command-wrapper' }, [
						new ui.Combobox('/bin/sh', [
							'/bin/ash',
							'/bin/bash',
						], {id: 'console-command' }).render()
					]),
					E('label', { 'style': 'margin-right: 10px; margin-left: 20px;' }, _('User(-u)')),
					E('input', {
						'type': 'text',
						'id': 'console-uid',
						'class': 'cbi-input-text',
						'placeholder': 'e.g., root or user id',
						'style': 'width: 150px; margin-right: 10px;'
					}),
					E('label', { 'style': 'margin-right: 10px; margin-left: 20px;' }, _('Port:')),
					E('input', {
						'type': 'number',
						'id': 'console-port',
						'class': 'cbi-input-text',
						'value': '7682',
						'min': '1024',
						'max': '65535',
						'style': 'width: 100px; margin-right: 10px;'
					}),
					E('button', {
						'class': 'cbi-button cbi-button-positive',
						'id': 'console-connect-btn',
						'click': () => this.connectConsole(this_container.Id)
					}, _('Connect')),
				]),
				E('div', {
					'id': 'console-frame-container',
					'style': 'display: none; margin-top: 15px;'
				}, [
					E('div', { 'style': 'margin-bottom: 10px;' }, [
						E('button', {
							'class': 'cbi-button cbi-button-negative',
							'click': () => this.disconnectConsole()
						}, _('Disconnect')),
						E('span', {
							'id': 'console-status',
							'style': 'margin-left: 10px; font-style: italic;'
						}, _('Connected to container console'))
					]),
					E('iframe', {
						'id': 'ttyd-frame',
						'class': 'xterm',
						'src': '',
						'style': 'width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 3px;'
					})
				])
			]);

			return consoleDiv;
		}, this);

		// WEBSOCKET TAB
		s.tab('wsconsole', _('WebSocket'));

		dm2.js_api_ready.then(([apiAvailable, host]) => {
			// Wait for JS API availability check to complete
			// Check if JS API is available
			if (!apiAvailable) {
				return;
			}

			o = s.taboption('wsconsole', form.DummyValue, 'wsconsole_controls', _('WebSocket Console'));
			o.render = L.bind(function() {
				const status = this.getContainerStatus();
				const isRunning = status === 'running';

				if (!isRunning) {
					return E('div', { 'class': 'alert-message warning' },
						_('Container is not running. Cannot connect to WebSocket console.'));
				}
				const wsDiv = E('div', { 'class': 'cbi-section' }, [
					E('div', { 'style': 'margin-bottom: 10px;' }, [
						E('label', { 'style': 'margin-right: 10px;' }, _('Streams:')),
						E('label', { 'style': 'margin-right: 6px;' }, [
							E('input', { 'type': 'checkbox', 'id': 'ws-stdin', 'checked': 'checked', 'style': 'margin-right: 4px;' }),
							_('Stdin')
						]),
						E('label', { 'style': 'margin-right: 6px;' }, [
							E('input', { 'type': 'checkbox', 'id': 'ws-stdout', 'checked': 'checked', 'style': 'margin-right: 4px;' }),
							_('Stdout')
						]),
						E('label', { 'style': 'margin-right: 6px;' }, [
							E('input', { 'type': 'checkbox', 'id': 'ws-stderr', 'style': 'margin-right: 4px;' }),
							_('Stderr')
						]),
						E('label', { 'style': 'margin-right: 6px;' }, [
							E('input', { 'type': 'checkbox', 'id': 'ws-logs', 'style': 'margin-right: 4px;' }),
							_('Include logs')
						]),
						E('button', {
							'class': 'cbi-button cbi-button-positive',
							'id': 'ws-connect-btn',
							'click': () => this.connectWebsocketConsole()
						}, _('Connect')),
						E('button', {
							'class': 'cbi-button cbi-button-neutral',
							'click': () => this.disconnectWebsocketConsole(),
							'style': 'margin-left: 6px;'
						}, _('Disconnect')),
						E('span', { 'id': 'ws-console-status', 'style': 'margin-left: 10px; color: #666;' }, _('Disconnected')),
					]),
					E('div', {
						'id': 'ws-console-output',
						'style': 'height: 320px; border: 1px solid #ccc; border-radius: 3px; padding: 8px; background:#111; color:#0f0; font-family: monospace; overflow: auto; white-space: pre-wrap;'
					}, ''),
					E('div', { 'style': 'margin-top: 10px; display: flex; gap: 6px;' }, [
						E('textarea', {
							'id': 'ws-console-input',
							'rows': '3',
							'placeholder': _('Type command here... (Ctrl+D to detach)'),
							'style': 'flex: 1; padding: 6px; font-family: monospace; resize: vertical;',
							'keydown': (ev) => {
								if (ev.key === 'Enter' && !ev.shiftKey) {
									ev.preventDefault();
									this.sendWebsocketInput();
								} else if (ev.key === 'd' && ev.ctrlKey) {
									ev.preventDefault();
									this.sendWebsocketDetach();
								}
							}
						}),
						E('button', {
							'class': 'cbi-button cbi-button-positive',
							'click': () => this.sendWebsocketInput()
						}, _('Send'))
					])
				]);

				return wsDiv;
			}, this);
		});

		// LOGS TAB
		s.tab('logs', _('Logs'));
		let logsDiv = null;
		let logsLoaded = false;

		o = s.taboption('logs', form.DummyValue, 'log_controls', _('Log Controls'));
		o.render = L.bind(() => {
			if (logsDiv) {
				return logsDiv;
			}

			logsDiv = E('div', { 'class': 'cbi-section' }, [
				E('div', { 'style': 'margin-bottom: 10px;' }, [
					E('label', { 'style': 'margin-right: 10px;' }, _('Lines to show:')),
					E('input', {
						'type': 'number',
						'id': 'log-lines',
						'class': 'cbi-input-text',
						'value': '100',
						'min': '1',
						'style': 'width: 80px;'
					}),
					E('button', {
						'class': 'cbi-button cbi-button-positive',
						'style': 'margin-left: 10px;',
						'click': () => this.loadLogs(this_container.Id)
					}, _('Load Logs')),
					E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'style': 'margin-left: 5px;',
						'click': () => this.clearLogs()
					}, _('Clear')),
				]),
				E('div', {
					'id': 'container-logs-text',
					'style': 'width: 100%; font-family: monospace; padding: 10px; border: 1px solid #ccc; overflow: auto;',
					'innerHTML': ''
				})
			]);

			return logsDiv;
		}, this);

		o = s.taboption('logs', form.DummyValue, 'log_display', _('Container Logs'));
		o.render = L.bind(() => {
			// Auto-load logs when tab is first accessed
			if (!logsLoaded) {
				logsLoaded = true;
				this.loadLogs();
			}
			return E('div');
		}, this);

		this.map = m;

		// Render the form and add buttons above it
		return m.render()
			.then(fe => {
				mainContainer.appendChild(fe);

				poll.add(L.bind(() => {
					if (this.getContainerStatus(this_container) !== 'running')
						return Promise.resolve();

					return dm2.container_changes({ id: this_container.Id })
						.then(L.bind(function(res) {
							if (res.code < 300 && Array.isArray(res.body)) {
								// Update changes table using L.ui.Table.update()
								if (this.changesTable) {
									const rows = res.body.map(change => change ? [
										ChangeTypes[change?.Kind] || change?.Kind,
										change?.Path
									] : []);
									this.changesTable.update(rows);
								}

								// Update the raw JSON field
								const changesField = document.getElementById('raw-changes-field');
								if (changesField) {
									changesField.textContent = JSON.stringify(res.body, null, 2);
								}
							}
						}, this))
						.catch(err => {
							console.error('Failed to poll container changes', err);
							return null;
						});
				}, this), 5);

				// Auto-refresh Stats table every 5 seconds (if container is running)
				poll.add(L.bind(() => {
					if (this.getContainerStatus(this_container) !== 'running')
						return Promise.resolve();

					return dm2.container_stats({ id: this_container.Id, query: { 'stream': false, 'one-shot': true } })
						.then(L.bind(function(res) {
							if (res.code < 300 && res.body) {
								return updateStats(res.body);
							}
						}, this))
						.catch(err => {
							console.error('Failed to poll container stats', err);
							return null;
						});
				}, this), 5);

				// Auto-refresh PS table every 5 seconds (if container is running)
				poll.add(L.bind(() => {
					if (this.getContainerStatus(this_container) !== 'running')
						return Promise.resolve();

					return dm2.container_top({ id: this_container.Id, query: { 'ps_args': this.psArgs || '-ww' } })
						.then(L.bind(function(res) {
							if (res.code < 300 && res.body && res.body.Processes) {
								// Check if titles changed - if so, rebuild the table
								if (res.body.Titles && JSON.stringify(res.body.Titles) !== JSON.stringify(this.psTitles)) {
									// Titles changed, need to recreate table
									this.psTitles = res.body.Titles;
									const psTableEl = document.getElementById('ps-table');
									if (psTableEl && psTableEl.parentNode) {
										const newTable = new L.ui.Table(
											res.body.Titles.map(t => _(t)),
											{ id: 'ps-table' },
											E('em', [_('No processes running')])
										);
										newTable.update(res.body.Processes);
										this.psTable = newTable;
										psTableEl.parentNode.replaceChild(newTable.render(), psTableEl);
									}
								} else if (this.psTable) {
									// Titles same, just update data
									this.psTable.update(res.body.Processes);
								}

								// Update raw JSON field
								const psField = document.getElementById('raw-ps-field');
								if (psField) {
									psField.textContent = JSON.stringify(res.body, null, 2);
								}
							}
						}, this))
						.catch(err => {
								console.error('Failed to poll container processes', err);
								return null;
							});
				}, this), 5);

				return mainContainer;
			});
	},

	handleSave(ev) {
		ev?.preventDefault();

		const map = this.map;
		if (!map)
			return Promise.reject(new Error(_('Form is not ready yet.')));

		// const listToKv = view.listToKv;

		const get = (opt) => map.data.get('json', 'cont', opt);
		// const getn = (opt) => map.data.get('json', 'nets', opt);
		const gethc = (opt) => map.data.get('json', 'hostcfg', opt);
		const toBool = (val) => (val === 1 || val === '1' || val === true);
		const toInt = (val) => val ? Number.parseInt(val) : undefined;
		// const toFloat = (val) => val ? Number.parseFloat(val) : undefined;

		// First: update properties
		map.parse()
			.then(() => {
				const this_container = map.data.get('json', 'cont');
				const id = this_container?.Id;
				/* In the container edit context, there are not many items we
				can change - duplicate the container */
				const createBody = {

					CpuShares: toInt(gethc('CpuShares')),
					Memory: toInt(gethc('Memory')),
					MemorySwap: toInt(gethc('MemorySwap')),
					MemoryReservation: toInt(gethc('MemoryReservation')),
					BlkioWeight: toInt(gethc('blkio_weight')),

					CpuPeriod: toInt(gethc('CpuPeriod')),
					CpuQuota: toInt(gethc('CpuQuota')),
					NanoCPUs: toInt(gethc('NanoCpus') * (10 ** 9)), // unit: 10^-9, input: float
					OomKillDisable: toBool(gethc('OomKillDisable')),

					RestartPolicy: { Name: get('restart_policy') || this_container.HostConfig?.RestartPolicy?.Name },

				};

				return { id, createBody };
			})
			.then(({ id, createBody }) => dm2.container_update({ id: id, body: createBody}))
			.then((response) => {
				if (response?.code >= 300) {
					ui.addTimeLimitedNotification(_('Container update failed'), [response?.body?.message || _('Unknown error')], 7000, 'warning');
					return false;
				}

				const msgTitle = _('Updated');
				if (response?.body?.Warnings)
					ui.addTimeLimitedNotification(msgTitle + _(' with warnings'), [response?.body?.Warnings], 5000);
				else
					ui.addTimeLimitedNotification(msgTitle, [ _('OK') ], 4000, 'info');

				if (get('Name') === null)
					setTimeout(() => window.location.href = `${this.dockerman_url}/containers`, 1000);

				return true;
			})
			.catch((err) => {
				ui.addTimeLimitedNotification(_('Container update failed'), [err?.message || err], 7000, 'warning');
				return false;
			});

		// Then: update name (separate operation)
		return map.parse()
			.then(() => {
				const this_container = map.data.get('json', 'cont');
				const name = this_container.Name || get('Name');
				const id = this_container.Id || get('Id');

				return { id, name };
			})
			.then(({ id, name }) => dm2.container_rename({ id: id, query: { name: name } }))
			.then((response) => {
				this.handleDockerResponse(response, _('Container rename'), {
					showOutput: false,
					showSuccess: false
				});

				return setTimeout(() => window.location.href = `${this.dockerman_url}/containers`, 1000);
			})
			.catch((err) => {
				this.showNotification(_('Container rename failed'), err?.message || String(err), 7000, 'error');
				return false;
			});
	},

	connectWebsocketConsole() {
		const connectBtn = document.getElementById('ws-connect-btn');
		const statusEl = document.getElementById('ws-console-status');
		const outputEl = document.getElementById('ws-console-output');
		const view = this;

		if (connectBtn) connectBtn.disabled = true;
		if (statusEl) statusEl.textContent = _('Connecting…');

		// Clear the output buffer when connecting anew
		if (outputEl) outputEl.innerHTML = '';

		// Initialize input buffer
		this.consoleInputBuffer = '';

		// Tear down any previous hijack or websocket without user-facing noise
		if (this.hijackController) {
			try { this.hijackController.abort(); } catch (e) {}
			this.hijackController = null;
		}
		if (this.consoleWs) {
			try {
				this.consoleWs.onclose = null;
				this.consoleWs.onerror = null;
				this.consoleWs.onmessage = null;
				this.consoleWs.close();
			} catch (e) {}
			this.consoleWs = null;
		}

		const stdin = document.getElementById('ws-stdin')?.checked ? '1' : '0';
		const stdout = document.getElementById('ws-stdout')?.checked ? '1' : '0';
		const stderr = document.getElementById('ws-stderr')?.checked ? '1' : '0';
		const logs = document.getElementById('ws-logs')?.checked ? '1' : '0';
		const stream = '1';

		const params = {
			stdin: stdin,
			stdout: stdout,
			stderr: stderr,
			logs: logs,
			stream: stream,
			detachKeys: 'ctrl-d',
		}

		dm2.container_attach_ws({ id: this.container.Id, query: params })
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			// Get the WebSocket connection
			const ws = response.ws || response.body;
			let opened = false;

			if (!ws || ws.readyState === undefined) {
				throw new Error('No WebSocket connection');
			}

			// Expect binary frames from Docker hijack; decode as UTF-8 text
			ws.binaryType = 'arraybuffer';

			// Set up WebSocket message handler
			ws.onmessage = (event) => {
				try {
					const renderAndAppend = (t) => {
						if (outputEl && t) {
							outputEl.innerHTML += dm2.ansiToHtml(t);
							outputEl.scrollTop = outputEl.scrollHeight;
						}
					};

					let text = '';
					const data = event.data;

					if (typeof data === 'string') {
						text = data;
					} else if (data instanceof ArrayBuffer) {
						text = new TextDecoder('utf-8').decode(new Uint8Array(data));
					} else if (data instanceof Blob) {
						// Fallback for Blob frames
						const reader = new FileReader();
						reader.onload = () => {
							const buf = reader.result;
							const t = new TextDecoder('utf-8').decode(new Uint8Array(buf));
							renderAndAppend(t);
						};
						reader.readAsArrayBuffer(data);
						return;
					}

					renderAndAppend(text);
				} catch (e) {
					console.error('Error processing message:', e);
				}
			};

			// Set up WebSocket error handler
			ws.onerror = (error) => {
				console.error('WebSocket error:', error);
				if (statusEl) statusEl.textContent = _('Error');
				view.showNotification(_('Error'), _('WebSocket error'), 7000, 'error');
				if (ws === view.consoleWs) {
					view.consoleWs = null;
				}
			};

			// Set up WebSocket close handler
			ws.onclose = (evt) => {
				if (!opened) return; // Suppress close noise from previous/failed sockets
				if (statusEl) statusEl.textContent = _('Disconnected');
				if (connectBtn) connectBtn.disabled = false;
				if (ws === view.consoleWs) {
					view.consoleWs = null;
				}
				const code = evt?.code;
				const reason = evt?.reason;
				view.showNotification(_('Info'), _('Console connection closed') + (code ? ` (code: ${code}${reason ? ', ' + reason : ''})` : ''), 3000, 'info');
			};

			ws.onopen = () => {
				opened = true;
				if (statusEl) statusEl.textContent = _('Connected');
				if (connectBtn) connectBtn.disabled = false;
				view.showNotification(_('Success'), _('Console connected'), 3000, 'info');

				// Store WebSocket reference so it doesn't get garbage collected
				view.consoleWs = ws;
			};

			// If already open (promise resolved after onopen), set state immediately
			if (ws.readyState === WebSocket.OPEN) {
				opened = true;
				view.consoleWs = ws;
				if (statusEl) statusEl.textContent = _('Connected');
				if (connectBtn) connectBtn.disabled = false;
			}
		})
		.catch(err => {
			if (err.name === 'AbortError') {
				if (statusEl) statusEl.textContent = _('Disconnected');
			} else {
				if (statusEl) statusEl.textContent = _('Error');
				view.showNotification(_('Error'), err?.message || String(err), 7000, 'error');
			}
			if (connectBtn) connectBtn.disabled = false;
			view.hijackController = null;
		});
	},

	disconnectWebsocketConsole() {
		const statusEl = document.getElementById('ws-console-status');
		const connectBtn = document.getElementById('ws-connect-btn');

		if (this.hijackController) {
			this.hijackController.abort();
			this.hijackController = null;
		}

		if (statusEl) statusEl.textContent = _('Disconnected');
		if (connectBtn) connectBtn.disabled = false;
		this.showNotification(_('Info'), _('Console disconnected'), 3000, 'info');
	},

	sendWebsocketInput() {
		const inputEl = document.getElementById('ws-console-input');
		if (!inputEl) return;

		const text = inputEl.value || '';

		// Check if WebSocket is actually connected
		if (this.consoleWs && this.consoleWs.readyState === WebSocket.OPEN) {
			try {
				const payload = text.endsWith('\n') ? text : `${text}\n`;
				this.consoleWs.send(payload);
				inputEl.value = '';
			} catch (e) {
				console.error('Error sending:', e);
				this.showNotification(_('Error'), _('Failed to send data'), 5000, 'error');
			}
		} else {
			this.showNotification(_('Error'), _('Console is not connected'), 5000, 'error');
		}
	},

	sendWebsocketDetach() {
		// Send ctrl-d (ASCII 4, EOT) to detach
		if (this.consoleWs && this.consoleWs.readyState === WebSocket.OPEN) {
			try {
				this.consoleWs.send('\x04');
				this.showNotification(_('Info'), _('Detach signal sent (Ctrl+D)'), 3000, 'info');
			} catch (e) {
				console.error('Error sending detach:', e);
				this.showNotification(_('Error'), _('Failed to send detach signal'), 5000, 'error');
			}
		} else {
			this.showNotification(_('Error'), _('Console is not connected'), 5000, 'error');
		}
	},

	handleFileUpload(container_id) {
		const path = document.getElementById('file-path')?.value || '/';

		const q_params = { path: encodeURIComponent(path) };

		return this.super('handleXHRTransfer', [{
			q_params: { query: q_params },
			method: 'PUT',
			commandCPath: `/container/archive/put/${container_id}/`,
			commandDPath: `/containers/${container_id}/archive`,
			commandTitle: _('Uploading…'),
			commandMessage: _('Uploading file to container…'),
			successMessage: _('File uploaded to') + ': ' + path,
			pathElementId: 'file-path',
			defaultPath: '/'
		}]);
	},

	handleFileDownload(container_id) {
		const path = document.getElementById('file-path')?.value || '/';
		const view = this;

		if (!path || path === '') {
			this.showNotification(_('Error'), _('Please specify a path'), 5000, 'error');
			return;
		}

		// Direct HTTP download bypassing RPC buffering
		window.location.href = `${this.dockerman_url}/container/archive/get/${container_id}` + `/?path=${encodeURIComponent(path)}`;
		return;
	},

	handleInfoArchive(container_id) {
		const path = document.getElementById('file-path')?.value || '/';
		const fileTextarea = document.getElementById('container-file-text');

		if (!fileTextarea) return;

		return dm2.container_info_archive({ id: container_id, query: { path: path } })
			.then((response) => {
				if (response?.code >= 300) {
					fileTextarea.value = _('Path error') + '\n' + (response?.body?.message || _('Unknown error'));
					this.showNotification(_('Error'), [response?.body?.message || _('Path error')], 7000, 'error');
					return false;
				}

				// check response?.headers?.entries?.length in case fetch API is used 
				if (!response.headers || response?.headers?.entries?.length == 0) return true;

				let fileInfo;
				try {
					fileInfo = JSON.parse(atob(response?.headers?.get?.('x-docker-container-path-stat') || response?.headers?.['x-docker-container-path-stat']));
					fileTextarea.value = 
						`name: ${fileInfo?.name}\n` +
						`size: ${fileInfo?.size}\n` +
						`mode: ${this.modeToRwx(fileInfo?.mode)}\n` +
						`mtime: ${fileInfo?.mtime}\n` +
						`linkTarget: ${fileInfo?.linkTarget}\n`;
				} catch {
					this.showNotification(_('Missing header or CORS interfering'), ['X-Docker-Container-Path-Stat'], 5000, 'notice');
				}

				return true;
			})
			.catch((err) => {
				const errorMsg = err?.message || String(err) || _('Path error');
				fileTextarea.value = _('Path error') + '\n' + errorMsg;
				this.showNotification(_('Error'), [errorMsg], 7000, 'error');
				return false;
			});
	},

	loadLogs(container_id) {
		const lines = parseInt(document.getElementById('log-lines')?.value || '100');
		const logsDiv = document.getElementById('container-logs-text');

		if (!logsDiv) return;

		logsDiv.innerHTML = '<em style="color: #999;">' + _('Loading logs…') + '</em>';

		return dm2.container_logs({ id: container_id, query: { tail: lines, stdout: true, stderr: true } })
			.then((response) => {
				if (response?.code >= 300) {
					logsDiv.innerHTML = '<span style="color: #ff5555;">' + _('Error loading logs:') + '</span><br/>' + 
						(response?.body?.message || _('Unknown error'));
					this.showNotification(_('Error'), response?.body?.message || _('Failed to load logs'), 7000, 'error');
					return false;
				}

				const logText = response?.body || _('No logs available');
				// Convert ANSI codes to HTML and set innerHTML
				logsDiv.innerHTML = dm2.ansiToHtml(logText);
				logsDiv.scrollTop = logsDiv.scrollHeight;
				return true;
			})
			.catch((err) => {
				const errorMsg = err?.message || String(err) || _('Failed to load logs');
				logsDiv.innerHTML = '<span style="color: #ff5555;">' + _('Error loading logs:') + '</span><br/>' + errorMsg;
				this.showNotification(_('Error'), errorMsg, 7000, 'error');
				return false;
			});
	},

	clearLogs() {
		const logsDiv = document.getElementById('container-logs-text');
		if (logsDiv) {
			logsDiv.innerHTML = '';
		}
	},

	connectConsole(container_id) {
		const commandWrapper = document.getElementById('console-command');
		const selectedItem = commandWrapper?.querySelector('li[selected]');
		const command = selectedItem?.textContent?.trim() || '/bin/sh';
		const uid = document.getElementById('console-uid')?.value || '';
		const port = parseInt(document.getElementById('console-port')?.value || '7682');
		const view = this;

		const connectBtn = document.getElementById('console-connect-btn');
		if (connectBtn) connectBtn.disabled = true;

		// Call RPC to start ttyd
		return dm2.container_ttyd_start({
			id: container_id,
			cmd: command,
			port: port,
			uid: uid
		})
		.then((response) => {
			if (connectBtn) connectBtn.disabled = false;

			if (response?.code >= 300) {
				const errorMsg = response?.body?.error || response?.body?.message || _('Failed to start console');
				view.showNotification(_('Error'), errorMsg, 7000, 'error');
				return false;
			}

			// Show iframe and set source
			const frameContainer = document.getElementById('console-frame-container');
			if (frameContainer) {
				frameContainer.style.display = 'block';
				const ttydFrame = document.getElementById('ttyd-frame');
				if (ttydFrame) {
					// Wait for ttyd to fully start and be ready for connections
					// Use a retry pattern to handle timing variations
					const waitForTtydReady = (attempt = 0, maxAttempts = 5, initialDelay = 500) => {
						const delay = initialDelay + (attempt * 200); // Increase delay on retries

						setTimeout(() => {
							const protocol = window.location.protocol === 'https:' ? 'https' : 'http';
							const ttydUrl = `${protocol}://${window.location.hostname}:${port}`;

							// Test connection with a simple HEAD request
							fetch(ttydUrl, { method: 'HEAD', mode: 'no-cors' })
								.then(() => {
									// Connection successful, load the iframe
									ttydFrame.src = ttydUrl;
								})
								.catch(() => {
									// Connection failed, retry if we haven't exceeded max attempts
									if (attempt < maxAttempts - 1) {
										waitForTtydReady(attempt + 1, maxAttempts, initialDelay);
									} else {
										// Max retries exceeded, load iframe anyway
										ttydFrame.src = ttydUrl;
										view.showNotification(_('Warning'), _('TTYd may still be starting up'), 5000, 'warning');
									}
								});
						}, delay);
					};

					waitForTtydReady();
				}
			}

			view.showNotification(_('Success'), _('Console connected'), 3000, 'info');
			return true;
		})
		.catch((err) => {
			if (connectBtn) connectBtn.disabled = false;
			const errorMsg = err?.message || String(err) || _('Failed to connect to console');
			view.showNotification(_('Error'), errorMsg, 7000, 'error');
			return false;
		});
	},

	disconnectConsole() {
		const frameContainer = document.getElementById('console-frame-container');
		if (frameContainer) {
			frameContainer.style.display = 'none';
			const ttydFrame = document.getElementById('ttyd-frame');
			if (ttydFrame) {
				ttydFrame.src = '';
			}
		}

		this.showNotification(_('Info'), _('Console disconnected'), 3000, 'info');
	},

	executeAction(ev, action, container_id) {
		ev?.preventDefault();

		const actionMap = Object.freeze({
			'start': _('Start'),
			'restart': _('Restart'),
			'stop': _('Stop'),
			'kill': _('Kill'),
			'pause': _('Pause'),
			'unpause': _('Unpause'),
			'remove': _('Remove'),
		});

		const actionLabel = actionMap[action] || action;

		// Confirm removal
		if (action === 'remove') {
			if (!confirm(_('Remove container?'))) {
				return;
			}
		}

		const view = this;
		const methodName = 'container_' + action;
		const method = dm2[methodName];

		if (!method) {
			view.showNotification(_('Error'), _('Action unavailable: ') + action, 7000, 'error');
			return;
		}

		view.executeDockerAction(
			method,
			{ id: container_id, query: {} },
			actionLabel,
			{
				showOutput: false,
				showSuccess: true,
				successMessage: actionLabel + _(' completed'),
				successDuration: 5000,
				onSuccess: () => {
					if (action === 'remove') {
						setTimeout(() => window.location.href = `${this.dockerman_url}/containers`, 1000);
					} else {
						setTimeout(() => location.reload(), 1000);
					}
				}
			}
		);
	},

	executeNetworkAction(action, networkID, networkName, this_container) {
		const view = this;

		if (action === 'disconnect') {
			if (!confirm(_('Disconnect network "%s" from container?').format(networkName))) {
				return;
			}

			view.executeDockerAction(
				dm2.network_disconnect,
				{
					id: networkID,
					body: { Container: view.containerId, Force: false }
				},
				_('Disconnect network'),
				{
					showOutput: false,
					showSuccess: true,
					successMessage: _('Network disconnected'),
					successDuration: 5000,
					onSuccess: () => {
						setTimeout(() => location.reload(), 1000);
					}
				}
			);
		} else if (action === 'connect') {
			const newNetworks = this.networks.filter(n => !Object.keys(this_container.NetworkSettings?.Networks || {}).includes(n.Name));

			if (newNetworks.length === 0) {
				view.showNotification(_('Info'), _('No additional networks available to connect'), 5000, 'info');
				return;
			}

			// Create modal dialog for selecting network
			const networkSelect = E('select', { 
				'id': 'network-select',
				'class': 'cbi-input-select',
				'style': 'width:100%; margin-top:10px;'
			}, newNetworks.map(n => {
				const subnet0 = n?.IPAM?.Config?.[0]?.Subnet;
				const subnet1 = n?.IPAM?.Config?.[1]?.Subnet;
				return E('option', { 'value': n.Id }, [`${n.Name}${n?.Driver ? ' | ' + n.Driver : ''}${subnet0 ? ' | ' + subnet0 : ''}${subnet1 ? ' | ' + subnet1 : ''}`]);
			}));

			const ip4Input = E('input', {
				'type': 'text',
				'id': 'network-ip',
				'class': 'cbi-input-text',
				'placeholder': 'e.g., 172.18.0.5',
				'style': 'width:100%; margin-top:5px;'
			});

			const ip6Input = E('input', {
				'type': 'text',
				'id': 'network-ip',
				'class': 'cbi-input-text',
				'placeholder': 'e.g., 2001:db8:1::1',
				'style': 'width:100%; margin-top:5px;'
			});

			const modalBody = E('div', { 'class': 'cbi-section' }, [
				E('p', {}, _('Select network to connect:')),
				networkSelect,
				E('label', { 'style': 'display:block; margin-top:10px;' }, _('IP Address (optional):')),
				ip4Input,
				ip6Input,
			]);

			ui.showModal(_('Connect Network'), [
				modalBody,
				E('div', { 'class': 'right' }, [
					E('button', {
						'class': 'cbi-button cbi-button-neutral',
						'click': ui.hideModal
					}, _('Cancel')),
					' ',
					E('button', {
						'class': 'cbi-button cbi-button-positive',
						'click': () => {
							const selectedNetwork = networkSelect.value;
							const ip4Address = ip4Input.value || '';
							// const ip6Address = ip6Input.value || '';

							if (!selectedNetwork) {
								view.showNotification(_('Error'), [_('No network selected')], 5000, 'error');
								return;
							}

							ui.hideModal();

							const body = { Container: view.containerId };
							body.EndpointConfig = { IPAMConfig: { IPv4Address: ip4Address } }; //, IPv6Address: ip6Address || null

							view.executeDockerAction(
								dm2.network_connect,
								{ id: selectedNetwork, body: body },
								_('Connect network'),
								{
									showOutput: false,
									showSuccess: true,
									successMessage: _('Network connected'),
									successDuration: 5000,
									onSuccess: () => {
										setTimeout(() => location.reload(), 1000);
									}
								}
							);
						}
					}, _('Connect'))
				])
			]);
		}
	},

	// handleSave: null,
	handleSaveApply: null,
	handleReset: null,

});

```

---

# container_new.js
```javascript
'use strict';
'require form';
'require fs';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/

/* API v1.52

POST /containers/create no longer supports configuring a container-wide MAC
address via the container's Config.MacAddress field. A container's MAC address
can now only be configured via endpoint settings when connecting to a network.

*/

return dm2.dv.extend({
	load() {
		const requestPath = L.env.requestpath;
		const duplicateId = requestPath[requestPath.length-1];
		const isDuplicate = requestPath[requestPath.length-2] === 'duplicate' && duplicateId;

		const promises = [
			dm2.image_list().then(images => {
				return images.body || [];
			}),
			dm2.network_list().then(networks => {
				return networks.body || [];
			}),
			dm2.volume_list().then(volumes => {
				return volumes.body?.Volumes || [];
			}),
			dm2.docker_info().then(info => {
				const numcpus = info.body?.NCPU || 1.0;
				const memory = info.body?.MemTotal || 2**10;
				return {numcpus: numcpus, memory: memory};
			}),
		];

		if (isDuplicate) {
			promises.push(
				dm2.container_inspect({ id: duplicateId }).then(container => {
					this.duplicateContainer = container.body || {};
					this.isDuplicate = true;
				})
			);
		}

		return Promise.all(promises);
	},

	render([image_list, network_list, volume_list, cpus_mem]) {
		this.volumes = volume_list;
		const view = this; // Capture the view context

		// Load duplicate container config if available
		let containerData = {container: {}};
		let pageTitle = _('Create new docker container');

		if (this.isDuplicate && this.duplicateContainer) {
			pageTitle = _('Duplicate/Edit Container: %s').format(this.duplicateContainer.Name?.substring(1) || '');
			const resolveImageId = (imageRef) => {
				if (!imageRef) return null;
				const match = (image_list || []).find(img => img.Id === imageRef || (Array.isArray(img.RepoTags) && img.RepoTags.includes(imageRef)));
				return match?.Id || null;
			};
			const c = this.duplicateContainer;
			const hostConfig = c.HostConfig || {};
			const resolvedImage = resolveImageId(c.Image) || resolveImageId(c.Config?.Image) || c.Image || c.Config?.Image || '';
			const builtInNetworks = new Set(['none', 'bridge', 'host']);
			const [netnames, nets] = Object.entries(c.NetworkSettings?.Networks || {});

			containerData.container = {
				name: c.Name?.substring(1) || '',
				interactive: c.Config?.AttachStdin ? 1 : 0,
				tty: c.Config?.Tty ? 1 : 0,
				image: resolvedImage,
				privileged: hostConfig.Privileged ? 1 : 0,
				restart_policy: hostConfig.RestartPolicy?.Name || 'unless-stopped',
				network: (() => {
					return (netnames && (netnames.length > 0)) ? netnames[0] : '';
				})(),
				ipv4: (() => {
					if (builtInNetworks.has(netnames[0])) return '';
					return (nets && (nets.length > 0)) ? nets[0]?.IPAddress || '' : '';
				})(),
				ipv6: (() => {
					if (builtInNetworks.has(netnames[0])) return '';
					return (nets && (nets.length > 0)) ? nets[0]?.GlobalIPv6Address || '' : '';
				})(),
				ipv6_lla: (() => {
					if (builtInNetworks.has(netnames[0])) return '';
					return (nets && (nets.length > 0)) ? nets[0]?.LinkLocalIPv6Address || '' : '';
				})(),
				link: hostConfig.Links || [],
				dns: hostConfig.Dns || [],
				user: c.Config?.User || '',
				env: c.Config?.Env || [],
				volume: (hostConfig.Mounts || c.Mounts || []).map(m => {
					let source;
					const destination = m.Destination || m.Target || '';
					let opts = '';
					if (m.Type === 'image') {
						source = '@image';
						if (m.ImageOptions && m.ImageOptions.Subpath)
							opts = 'subpath=' + m.ImageOptions.Subpath;
					} else if (m.Type === 'tmpfs') {
						source = '@tmpfs';
						const tmpOpts = [];
						if (m.TmpfsOptions) {
							if (m.TmpfsOptions.SizeBytes) tmpOpts.push('size=' + m.TmpfsOptions.SizeBytes);
							if (m.TmpfsOptions.Mode) tmpOpts.push('mode=' + m.TmpfsOptions.Mode);
							if (Array.isArray(m.TmpfsOptions.Options)) {
								for (const o of m.TmpfsOptions.Options) {
									if (Array.isArray(o) && o.length === 2) tmpOpts.push(`${o[0]}=${o[1]}`);
									else if (Array.isArray(o) && o.length === 1) tmpOpts.push(o[0]);
								}
							}
						}
						opts = tmpOpts.join(',');
					} else if (m.Type === 'volume') {
						source = m.Source || '';
						// opts = m.Mode || '';
					} else {
						source = m.Source || '';
						opts = m.Mode || '';
					}
					return source + ':' + destination + (opts ? ':' + opts : '');
				}),
				publish: (() => {
					const ports = [];
					for (const [containerPort, bindings] of Object.entries(hostConfig.PortBindings || {})) {
						if (Array.isArray(bindings) && bindings.length > 0 && bindings[0]?.HostPort) {
							const hostPort = bindings[0].HostPort;
							ports.push(hostPort + ':' + containerPort);
						}
					}
					return ports;
				})(),
				command: c.Config?.Cmd ? c.Config?.Cmd.join(' ') : '',
				hostname: c.Config?.Hostname || '',
				publish_all: hostConfig.PublishAllPorts ? 1 : 0,
				device: (hostConfig.Devices || []).map(d => d.PathOnHost + ':' + d.PathInContainer + (d.CgroupPermissions ? ':' + d.CgroupPermissions : '')),
				tmpfs: (() => {
					const list = [];
					if (hostConfig.Tmpfs && typeof hostConfig.Tmpfs === 'object') {
						for (const [path, opts] of Object.entries(hostConfig.Tmpfs)) {
							list.push(path + (opts ? ':' + opts : ''));
						}
					}
					return list;
				})(),
				sysctl: (() => {
					const list = [];
					if (hostConfig.Sysctls && typeof hostConfig.Sysctls === 'object') {
						for (const [key, value] of Object.entries(hostConfig.Sysctls)) {
							list.push(key + ':' + value);
						}
					}
					return list;
				})(),
				cap_add: hostConfig.CapAdd || [],
				cpus: hostConfig.NanoCPUs ? (hostConfig.NanoCPUs / (10 ** 9)).toFixed(3) : '',
				cpu_shares: hostConfig.CpuShares || '',
				cpu_period: hostConfig.CpuPeriod || '',
				cpu_quota: hostConfig.CpuQuota || '',
				memory: hostConfig.Memory || '',
				memory_reservation: hostConfig.MemoryReservation || '',
				blkio_weight: hostConfig.BlkioWeight || '',
				log_opt: (() => {
					const list = [];
					const logConfig = hostConfig.LogConfig?.Config;
					if (logConfig && typeof logConfig === 'object') {
						for (const [key, value] of Object.entries(logConfig)) {
							list.push(key + '=' + value);
						}
					}
					return list;
				})(),
			};
		}

		// stuff JSONMap with container config
		const m = new form.JSONMap(containerData, _('Docker - Containers'));
		m.submit = true;
		m.reset = true;

		let s = m.section(form.NamedSection, 'container', pageTitle);
		s.anonymous = true;
		s.nodescriptions = true;
		s.addremove = false;

		let o;

		o = s.option(form.Value, 'name', _('Container Name'),
			_('Name of the container that can be selected during container creation'));
		o.rmempty = true;

		o = s.option(form.Flag, 'interactive', _('Interactive (-i)'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;

		o = s.option(form.Flag, 'tty', _('TTY (-t)'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;

		o = s.option(form.ListValue, 'image', _('Docker Image'));
		o.rmempty = true;
		for (const image of image_list) {
			o.value(image.Id, image?.RepoTags?.[0]);
		}

		o = s.option(form.Flag, 'pull', _('Always pull image first'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;

		o = s.option(form.Flag, 'privileged', _('Privileged'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;

		o = s.option(form.ListValue, 'restart_policy', _('Restart Policy'));
		o.rmempty = true;
		o.default = 'unless-stopped';
		o.value('no', _('No'));
		o.value('unless-stopped', _('Unless stopped'));
		o.value('always', _('Always'));
		o.value('on-failure', _('On failure'));

		o = s.option(form.ListValue, 'network', _('Networks'));
		o.rmempty = true;
		this.buildNetworkListValues(network_list, o);

		function not_with_a_docker_net(section_id, value) {
			if (!value || value === "") return true;
			const builtInNetworks = new Set(['none', 'bridge', 'host']);
			let dnet = this.section.getOption('network').getUIElement(section_id).getValue();
			const disallowed = builtInNetworks.has(dnet);
			if (disallowed) return _('Only for user-defined networks');
		};

		o = s.option(form.Value, 'ipv4', _('IPv4 Address'));
		o.rmempty = true;
		o.datatype = 'ip4addr';
		o.validate = not_with_a_docker_net;

		o = s.option(form.Value, 'ipv6', _('IPv6 Address'));
		o.rmempty = true;
		o.datatype = 'ip6addr';
		o.validate = not_with_a_docker_net;

		o = s.option(form.Value, 'ipv6_lla', _('IPv6 Link-Local Address'));
		o.rmempty = true;
		o.datatype = 'ip6ll';
		o.validate = not_with_a_docker_net;

		o = s.option(form.DynamicList, 'link', _('Links with other containers'));
		o.rmempty = true;
		o.placeholder='container_name:alias';

		o = s.option(form.DynamicList, 'dns', _('Set custom DNS servers'));
		o.rmempty = true;
		o.placeholder='8.8.8.8';

		o = s.option(form.Value, 'user', _('User(-u)'),
			_('The user that commands are run as inside the container. (format: name|uid[:group|gid])'));
		o.rmempty = true;
		o.placeholder='1000:1000';

		o = s.option(form.DynamicList, 'env', _('Environmental Variable(-e)'),
			_('Set environment variables inside the container'));
		o.rmempty = true;
		o.placeholder='TZ=Europe/Paris';

		o = s.option(form.DummyValue, 'volume', _('Mount(--mount)'),
			_('Bind mount a volume'));
		o.rmempty = true;
		o.cfgvalue = () => {
			const c_volumes = view.map.data.get('json', 'container', 'volume') || [];

			const showVolumeModal = (index, initialEntry) => {
				let typeSelect, bindPicker, bindSourceField, volumeNameInput, volumeSourceField, pathInput, pathField, optionsDropdown, optionsField, subpathInput;
				let tmpfsSizeInput, tmpfsModeInput, tmpfsOptsInput, tmpfsSizeField, tmpfsModeField, tmpfsOptsField;
				const isEdit = index !== null;
				const modalTitle = isEdit ? _('Edit Mount') : _('Add Mount');

					// Parse existing entry if editing and infer type from volumes list, image, or tmpfs
					let initialType = 'bind', initialSource = '', initialPath = '', initialOptions = '';
					if (isEdit && initialEntry) {
						const parts = (typeof initialEntry === 'string' ? initialEntry : '').split(':');
						initialSource = parts[0] || '';
						initialPath = parts[1] || '';
						initialOptions = parts[2] || '';
						// Infer type: tmpfs, volume, image, else bind
						const isTmpfs = (initialSource === '@tmpfs');
						const isVolume = (volume_list || []).some(v => v.Name === initialSource || v.Id === initialSource);
						const isImage = (initialSource === '@image');
						initialType = isTmpfs ? 'tmpfs' : (isVolume ? 'volume' : (isImage ? 'image' : 'bind'));
				}

				const existingOptions = (typeof initialOptions === 'string' ? initialOptions : '').split(',').map(o => o.trim()).filter(Boolean);

				// Type-specific options for dropdowns
				const bindOptions = {
					'ro': _('Read-only (ro)'),
					'rw': _('Read-write (rw)'),
					'private': _('Propagation: private'),
					'rprivate': _('Propagation: rprivate'),
					'shared': _('Propagation: shared'),
					'rshared': _('Propagation: rshared'),
					'slave': _('Propagation: slave'),
					'rslave': _('Propagation: rslave')
				};

				const volumeOptions = {
					// 'ro': _('Read-only (ro)'),
					// 'rw': _('Read-write (rw)'),
					'nocopy': _('No copy (nocopy)')
				};

				const getOptionsForType = (type) => type === 'bind' ? bindOptions : volumeOptions;

				const namesListId = 'volname-list-' + Math.random().toString(36).substr(2, 9);

				// Create dropdown for options - updates based on type
				optionsDropdown = new ui.Dropdown(existingOptions, getOptionsForType(initialType), {
					id: 'mount-options-' + Math.random().toString(36).substr(2, 9),
					multiple: true,
					optional: true,
					display_items: 2,
					placeholder: _('Select options...')
				});

				const createField = (label, input) => {
					return E('div', { 'class': 'cbi-value' }, [
						E('label', { 'class': 'cbi-value-title' }, label),
						E('div', { 'class': 'cbi-value-field' }, Array.isArray(input) ? input : [input])
					]);
				};

				// Type select
				const typeOptions = [
					E('option', { value: 'bind' }, _('Bind (host directory)')),
					E('option', { value: 'volume' }, _('Volume (named)')),
					E('option', { value: 'image' }, _('Image (from image)')),
					E('option', { value: 'tmpfs' }, _('Tmpfs'))
				];
				typeSelect = E('select', { 'class': 'cbi-input-select' }, typeOptions);
				typeSelect.value = initialType;

				// Bind directory picker using ui.FileUpload
				bindPicker = new ui.FileUpload(initialType === 'bind' ? initialSource : '', {
					browser: false,
					directory_select: true,
					directory_create: false,
					enable_upload: false,
					enable_remove: false,
					enable_download: false,
					root_directory: '/',
					show_hidden: true
				});

				// Volume name input with datalist
				volumeNameInput = E('input', {
					'type': 'text',
					'class': 'cbi-input-text',
					'placeholder': _('Enter volume name or pick existing'),
					'list': namesListId,
					'value': initialType === 'volume' ? initialSource : ''
				});
				volumeSourceField = createField(_('Volume Name'), [
					E('div', { 'style': 'position: relative;' }, [
						volumeNameInput,
						E('span', { 'style': 'pointer-events: none;' }, '▼')
					]),
					E('datalist', { 'id': namesListId }, [
						...volume_list.map(vol => E('option', { 'value': vol.Name }, vol.Name))
					])
				]);

				// Tmpfs inputs - pre-populate if editing
				let tmpfsSizeVal = '', tmpfsModeVal = '', tmpfsOptsVal = '';
				if (initialType === 'tmpfs' && existingOptions.length) {
					const rest = [];
					existingOptions.forEach(o => {
						if (o.startsWith('size=')) tmpfsSizeVal = o.slice('size='.length);
						else if (o.startsWith('mode=')) tmpfsModeVal = view.modeToRwx(o.slice('mode='.length));
						else rest.push(o);
					});
					tmpfsOptsVal = rest.join(',');
				}

				tmpfsSizeField = createField(_('Size'),
					tmpfsSizeInput = E('input', {
						'class': 'cbi-input-text',
						'placeholder': '128m',
						'value': tmpfsSizeVal
					})
				);
				tmpfsModeField = createField(_('Mode'),
					tmpfsModeInput = E('input', {
						'class': 'cbi-input-text',
						'placeholder': 'rwxr-xr-x or 1770',
						'value': tmpfsModeVal
					})
				);
				tmpfsOptsField = createField(_('tmpfs Options'),
					tmpfsOptsInput = E('input', {
						'type': 'text',
						'class': 'cbi-input-text',
						'placeholder': 'nr_blocks=blocks,...',
						'value': tmpfsOptsVal
					})
				);

				// Render bindPicker and show modal
				Promise.resolve(bindPicker.render()).then(bindPickerNode => {
					bindSourceField = createField(_('Host Directory'), bindPickerNode);

					const updateOptions = (selectedType) => {
						optionsField.querySelector('.cbi-value-field').innerHTML = '';
						if (selectedType === 'image') {
							// For image mounts, show a Subpath text input (only option)
							subpathInput = E('input', {
								'type': 'text',
								'class': 'cbi-input-text',
								'placeholder': _('/path/in/image'),
								'value': (initialType === 'image' && existingOptions.find(o => o.startsWith('subpath='))) ? existingOptions.find(o => o.startsWith('subpath=')).slice('subpath='.length) : ''
							});
							optionsField.querySelector('.cbi-value-title').textContent = _('Subpath');
							optionsField.querySelector('.cbi-value-field').appendChild(subpathInput);
						} else if (selectedType === 'tmpfs') {
							// Tmpfs fields are shown as main fields, hide options field
							optionsField.style.display = 'none';
						} else {
							optionsField.querySelector('.cbi-value-title').textContent = _('Options');
							// Recreate dropdown with new options
							const currentValue = optionsDropdown.getValue();
							optionsDropdown = new ui.Dropdown(currentValue, getOptionsForType(selectedType), {
								id: 'mount-options-' + Math.random().toString(36).substr(2, 9),
								multiple: true,
								optional: true,
								display_items: 2,
								placeholder: _('Select options...')
							});
							optionsField.querySelector('.cbi-value-field').appendChild(optionsDropdown.render());
							optionsField.style.display = '';
						}
					};

					const toggleSources = () => {
						const isBind = typeSelect.value === 'bind';
						const isVolume = typeSelect.value === 'volume';
						const isImage = typeSelect.value === 'image';
						const isTmpfs = typeSelect.value === 'tmpfs';
						bindSourceField.style.display = isBind ? '' : 'none';
						volumeSourceField.style.display = isVolume ? '' : 'none';
						pathField.style.display = isImage ? 'none' : '';
						tmpfsSizeField.style.display = isTmpfs ? '' : 'none';
						tmpfsModeField.style.display = isTmpfs ? '' : 'none';
						tmpfsOptsField.style.display = isTmpfs ? '' : 'none';
						updateOptions(typeSelect.value);
					};

					optionsField = createField(_('Options'), optionsDropdown.render());

					ui.showModal(modalTitle, [
						createField(_('Type'), typeSelect),
						bindSourceField,
						volumeSourceField,
						pathField = createField(_('Mount Path'),
							pathInput = E('input', {
								'type': 'text',
								'class': 'cbi-input-text',
								'placeholder': _('/mnt/path'),
								'value': initialPath
							})
						),
						tmpfsSizeField,
						tmpfsModeField,
						tmpfsOptsField,
						optionsField,
						E('div', { 'class': 'right' }, [
							E('button', {
								'class': 'cbi-button',
								'click': ui.hideModal
							}, [_('Cancel')]),
							' ',
							E('button', {
								'class': 'cbi-button cbi-button-positive',
								'click': ui.createHandlerFn(view, () => {
									const selectedType = typeSelect.value;
									const sourcePath = selectedType === 'bind'
										? (bindPicker.getValue() || '').trim()
										: (selectedType === 'volume'
											? (volumeNameInput.value || '').trim()
											: (selectedType === 'tmpfs' ? '@tmpfs' : '@image'));
									const subpathVal = (selectedType === 'image') ? (subpathInput?.value || '').trim() : '';
									const mountPath = (selectedType === 'image') ? subpathVal : pathInput.value.trim();
									let selectedOptions;
									if (selectedType === 'image') {
										selectedOptions = subpathVal ? ('subpath=' + subpathVal) : '';
									} else if (selectedType === 'tmpfs') {
										const opts = [];
										const sizeValRaw = (tmpfsSizeInput?.value || '').trim();
										const modeValRaw = (tmpfsModeInput?.value || '').trim();
										const extraVal = (tmpfsOptsInput?.value || '').trim();
										const parsedSize = sizeValRaw ? view.parseMemory(sizeValRaw) : undefined;
										const parsedMode = view.rwxToMode(modeValRaw);
										if (parsedSize) opts.push('size=' + parsedSize);
										else if (sizeValRaw) opts.push('size=' + sizeValRaw); // fallback if parse fails
										if (parsedMode !== undefined) opts.push('mode=' + parsedMode);
										if (extraVal) opts.push(...extraVal.split(',').map(o => o.trim()).filter(Boolean));
										selectedOptions = opts.join(',');
									} else {
										selectedOptions = optionsDropdown.getValue().join(',');
									}

									if (!sourcePath) {
										ui.addTimeLimitedNotification(null, [_('Please choose a directory or enter a volume name')], 3000, 'warning');
										return;
									}

									if (selectedType !== 'image' && !mountPath) {
										ui.addTimeLimitedNotification(null, [_('Please enter a mount path')], 3000, 'warning');
										return;
									}
									if (selectedType === 'image' && !subpathVal) {
										ui.addTimeLimitedNotification(null, [_('Please enter a subpath')], 3000, 'warning');
										return;
									}
									if (selectedType === 'tmpfs' && !mountPath) {
										ui.addTimeLimitedNotification(null, [_('Please enter a mount path')], 3000, 'warning');
										return;
									}

									ui.hideModal();

									const currentVolumes = view.map.data.get('json', 'container', 'volume') || [];
									const volumeEntry = selectedOptions ? (sourcePath + ':' + mountPath + ':' + selectedOptions) : (sourcePath + ':' + mountPath);
									let updatedVolumes;
									if (isEdit) {
										updatedVolumes = [...currentVolumes];
										updatedVolumes[index] = volumeEntry;
									} else {
										updatedVolumes = Array.isArray(currentVolumes) ? [...currentVolumes, volumeEntry] : [volumeEntry];
									}
									view.map.data.set('json', 'container', 'volume', updatedVolumes);

									return view.map.render();
								})
							}, [isEdit ? _('Update') : _('Add')])
						])
					]);

					toggleSources();
					typeSelect.addEventListener('change', toggleSources);
				});
			};


			return E('div', { 'class': 'cbi-dynlist' }, [
				...(c_volumes.length > 0 ? c_volumes.map((v, idx) => E('div', {
					'class': 'cbi-dynlist-item',
					'style': 'display: flex; justify-content: space-between; align-items: center; padding: 8px 5px; margin-bottom: 8px; gap: 10px;'
				}, [
					E('span', {
						'style': 'cursor: pointer; flex: 1;',
						'click': ui.createHandlerFn(view, () => {
							showVolumeModal(idx, v);
						})
					}, v),
					E('button', {
						'style': 'padding: 5px; color: #c44;',
						'class': 'cbi-button-negative remove',
						'title': _('Delete this volume mount'),
						'click': ui.createHandlerFn(view, () => {
							const currentVolumes = view.map.data.get('json', 'container', 'volume') || [];
							const updatedVolumes = currentVolumes.filter((_, i) => i !== idx);
							view.map.data.set('json', 'container', 'volume', updatedVolumes);
							return view.map.render();
						})
					}, ['✕'])
				])) : [E('div', { 'style': 'padding: 5px; color: #999;' }, _('No volumes available'))]),
				E('button', {
					'class': 'cbi-button',
					'click': ui.createHandlerFn(view, () => {
						showVolumeModal(null, null);
					})
				}, [_('Add Mount')])
			]);
		};
		o.rmempty = true;

		o = s.option(form.DynamicList, 'publish', _('Exposed Ports(-p)'),
			_("Publish container's port(s) to the host"));
		o.rmempty = true;
		o.placeholder='2200:22/tcp';

		o = s.option(form.Value, 'command', _('Run command'));
		o.rmempty = true;
		o.placeholder='/bin/sh init.sh';

		o = s.option(form.Flag, 'advanced', _('Advanced'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;

		o = s.option(form.Value, 'hostname', _('Host Name'),
			_('The hostname to use for the container'));
		o.rmempty = true;
		o.placeholder='/bin/sh init.sh';
		o.depends('advanced', 1);

		o = s.option(form.Flag, 'publish_all', _('Exposed All Ports(-P)'),
			_("Allocates an ephemeral host port for all of a container's exposed ports"));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;
		o.depends('advanced', 1);

		o = s.option(form.DynamicList, 'device', _('Device(--device)'),
			_('Add host device to the container'));
		o.rmempty = true;
		o.placeholder='/dev/sda:/dev/xvdc:rwm';
		o.depends('advanced', 1);

		o = s.option(form.DynamicList, 'tmpfs', _('Tmpfs(--tmpfs)'),
			_('Mount tmpfs directory'));
		o.rmempty = true;
		o.placeholder='/run:rw,noexec,nosuid,size=65536k';
		o.depends('advanced', 1);

		o = s.option(form.DynamicList, 'sysctl', _('Sysctl(--sysctl)'),
			_('Sysctls (kernel parameters) options'));
		o.rmempty = true;
		o.placeholder='net.ipv4.ip_forward=1';
		o.depends('advanced', 1);

		o = s.option(form.DynamicList, 'cap_add', _('CAP-ADD(--cap-add)'),
			_('A list of kernel capabilities to add to the container'));
		o.rmempty = true;
		o.placeholder='NET_ADMIN';
		o.depends('advanced', 1);

		o = s.option(form.Value, 'cpus', _('CPUs'),
			_('Number of CPUs. Number is a fractional number. 0.000 means no limit'));
		o.rmempty = true;
		o.placeholder='1.5';
		o.datatype = 'ufloat';
		o.depends('advanced', 1);
		o.validate = function(section_id, value) {
			if (!value) return true;
			if (value > cpus_mem.numcpus) return _(`Only ${cpus_mem.numcpus} CPUs available`);
			return true;
		};

		o = s.option(form.Value, 'cpu_period', _('CPU Period'),
			_('The length of a CPU period in microseconds'));
		o.rmempty = true;
		o.datatype = 'or(and(uinteger,min(1000),max(1000000)),"0")';
		o.depends('advanced', 1);

		o = s.option(form.Value, 'cpu_quota', _('CPU Quota'),
			_('Microseconds of CPU time that the container can get in a CPU period'));
		o.rmempty = true;
		o.datatype = 'uinteger';
		o.depends('advanced', 1);

		o = s.option(form.Value, 'cpu_shares', _('CPU Shares Weight'),
			_('CPU shares relative weight, if 0 is set, the system will ignore the value and use the default of 1024'));
		o.rmempty = true;
		o.placeholder='1024';
		o.datatype = 'uinteger';
		o.depends('advanced', 1);

		o = s.option(form.Value, 'memory', _('Memory'),
			_('Memory limit (format: <number>[<unit>]). Number is a positive integer. Unit can be one of b, k, m, or g. Minimum is 4M'));
		o.rmempty = true;
		o.placeholder = '128m';
		o.depends('advanced', 1);
		o.write = function(section_id, value) {
			if (!value || value == 0) return 0;
			this.map.data.data[section_id].memory = view.parseMemory(value);;
			return view.parseMemory(value);
		};
		o.validate = function(section_id, value) {
			if (!value) return true;
			if (value > view.memory) return _(`Only ${view.memory} bytes available`);
			return true;
		};

		o = s.option(form.Value, 'memory_reservation', _('Memory Reservation'));
		o.depends('advanced', 1);
		o.placeholder = '128m';
		o.cfgvalue = (sid, val) => {
			const res = view.map.data.data[sid].memory_reservation;
			return res ? '%1024.2m'.format(res) : 0;
		};
		o.write = function(section_id, value) {
			if (!value || value == 0) return 0;
			this.map.data.data[section_id].memory_reservation = view.parseMemory(value);;
			return view.parseMemory(value);
		};

		o = s.option(form.Value, 'blkio_weight', _('Block IO Weight'),
			_('Block IO weight (relative weight) accepts a weight value between 10 and 1000.'));
		o.rmempty = true;
		o.placeholder='500';
		o.datatype = 'and(uinteger,min(10),max(1000))';
		o.depends('advanced', 1);

		o = s.option(form.DynamicList, 'log_opt', _('Log driver options'),
			_('The logging configuration for this container'));
		o.rmempty = true;
		o.placeholder='max-size=1m';
		o.depends('advanced', 1);


		this.map = m;

		return m.render();

	},

	handleSave(ev) {
		ev?.preventDefault();
		const view = this; // Capture the view context
		const map = this.map;
		if (!map)
			return Promise.reject(new Error(_('Form is not ready yet.')));

		const listToKv = view.listToKv;

		const toBool = (val) => (val === 1 || val === '1' || val === true);
		const toInt = (val) => val ? Number.parseInt(val) : undefined;
		const toFloat = (val) => val ? Number.parseFloat(val) : undefined;

		return map.parse()
			.then(() => {
				const get = (opt) => map.data.get('json', 'container', opt);
				const name = get('name');
				// const pull = toBool(get('pull'));
				const network = get('network');
				const publish = get('publish');
				const command = get('command');
				// const publish_all = toBool(get('publish_all'));
				const device = get('device');
				const tmpfs = get('tmpfs');
				const sysctl = get('sysctl');
				const log_opt = get('log_opt');

				const createBody = {
					Hostname: get('hostname'),
					User: get('user'),
					AttachStdin: toBool(get('interactive')),
					Tty: toBool(get('tty')),
					OpenStdin: toBool(get('interactive')),
					Env: get('env'),
					Cmd: command ? command.split(' ') : null,
					Image: get('image'),
					HostConfig: {
						CpuShares: toInt(get('cpu_shares')),
						Memory: toInt(get('memory')),
						MemoryReservation: toInt(get('memory_reservation')),
						BlkioWeight: toInt(get('blkio_weight')),
						CapAdd: get('cap_add'),
						CpuPeriod: toInt(get('cpu_period')),
						CpuQuota: toInt(get('cpu_quota')),
						NanoCPUs: toFloat(get('cpus')) * (10 ** 9),
						Devices: device ? device
							.filter(d => d && typeof d === 'string' && d.trim().length > 0)
							.map(d => {
							const parts = d.split(':');
							return {
								PathOnHost: parts[0],
								PathInContainer: parts[1] || parts[0],
								CgroupPermissions: parts[2] || 'rwm'
							};
						}) : undefined,
						LogConfig: log_opt ? {
							Type: 'json-file',
							Config: listToKv(log_opt)
						} : undefined,
						NetworkMode: network,
						PortBindings: publish ? Object.fromEntries(
							(Array.isArray(publish) ? publish : [publish])
							.filter(p => p && typeof p === 'string' && p.trim().length > 0)
							.map(p => {
								const m = p.match(/^(\d+):(\d+)\/(tcp|udp)$/);
								if (m) return [`${m[2]}/${m[3]}`, [{ HostPort: m[1] }]];
								return null;
							}).filter(Boolean)
						) : undefined,
						Mounts: undefined,
						Links: get('link'),
						Privileged: toBool(get('privileged')),
						PublishAllPorts: toBool(get('publish_all')),
						RestartPolicy: { Name: get('restart_policy') },
						Dns: get('dns'),
						Tmpfs: tmpfs ? Object.fromEntries(
							(Array.isArray(tmpfs) ? tmpfs : [tmpfs])
							.filter(t => t && typeof t === 'string' && t.trim().length > 0)
							.map(t => {
								const parts = t.split(':');
								return [parts[0], parts[1] || ''];
							})
						) : undefined,
						Sysctls: sysctl ? listToKv(sysctl) : undefined,
					},
					NetworkingConfig: {
						EndpointsConfig: { [network]: { IPAMConfig: { IPv4Address: get('ipv4') || null, IPv6Address: get('ipv6') || null } } },
					}
				};

				// Parse volume entries and populate Mounts
				const volumeEntries = get('volume') || [];
				const volumeNames = new Set((view.volumes || []).map(v => v.Name));
				const volumeIds = new Set((view.volumes || []).map(v => v.Id));
				const mounts = [];
				for (const entry of volumeEntries) {
					let e = typeof entry === 'string' ? entry : '';
					let f = e.split(':')?.map(e => e && e.trim() || '');
					let source = f[0];
					let target = f[1];
					let options = f[2];

					if (!options) options = '';

					// Validate source and target are not empty
					if (!source || !target) {
						console.warn('Invalid volume entry (empty source or target):', entry);
						continue;
					}

					// Infer type: '@image' => image; '@tmpfs' => tmpfs; volume by name/id; else bind
					let type = 'bind';
					if (source === '@image') {
						type = 'image';
					} else if (source === '@tmpfs') {
						type = 'tmpfs';
					} else if (volumeNames.has(source) || volumeIds.has(source)) {
						type = 'volume';
					}

					const mount = {
						Type: type,
						Source: source,
						Target: target,
						ReadOnly: options.split(',').includes('ro')
					};

					// Add type-specific options
					if (type === 'bind') {
						const bindOptions = {};
						const propagation = options.split(',').find(opt => 
							['rprivate', 'private', 'rshared', 'shared', 'rslave', 'slave'].includes(opt)
						);
						if (propagation) bindOptions.Propagation = propagation;
						if (Object.keys(bindOptions).length > 0) mount.BindOptions = bindOptions;
					} else if (type === 'volume') {
						const volumeOptions = {};
						if (options.includes('nocopy')) volumeOptions.NoCopy = true;
						if (Object.keys(volumeOptions).length > 0) mount.VolumeOptions = volumeOptions;
					} else if (type === 'image') {
						const imageOptions = {};
						const subpathOpt = options.split(',').find(opt => opt.startsWith('subpath='));
						if (subpathOpt) imageOptions.Subpath = subpathOpt.slice('subpath='.length);
						if (Object.keys(imageOptions).length > 0) mount.ImageOptions = imageOptions;
						// Image source is implied by selected container image
						mount.Source = createBody.Image;
					} else if (type === 'tmpfs') {
						const tmpfsOptions = {};
						const optsList = options.split(',').map(o => o.trim()).filter(Boolean);
						for (const opt of optsList) {
							if (opt.startsWith('size=')) tmpfsOptions.SizeBytes = toInt(opt.slice('size='.length));
							else if (opt.startsWith('mode=')) tmpfsOptions.Mode = toInt(opt.slice('mode='.length));
							else {
								if (!tmpfsOptions.Options) tmpfsOptions.Options = [];
								const kv = opt.split('=');
								if (kv.length === 2) tmpfsOptions.Options.push([kv[0], kv[1]]);
								else if (kv.length === 1) tmpfsOptions.Options.push([kv[0]]);
							}
						}
						mount.Source = '';
						if (Object.keys(tmpfsOptions).length > 0) mount.TmpfsOptions = tmpfsOptions;
					}

					mounts.push(mount);
				}
				createBody.HostConfig.Mounts = mounts.length > 0 ? mounts : undefined;

				// Clean up undefined values
				Object.keys(createBody.HostConfig).forEach(key => {
					if (createBody.HostConfig[key] === undefined)
						delete createBody.HostConfig[key];
				});

				if (!name)
					return Promise.reject(new Error(_('No name specified.')));

				return { name, createBody };
			})
			.then(({ name, createBody }) => view.executeDockerAction(
				dm2.container_create,
				{ query: { name: name }, body: createBody },
				_('Create container'),
				{
					showOutput: false,
					showSuccess: false,
					onSuccess: (response) => {
						const isDuplicate = view.isDuplicate && view.duplicateContainer;
						const msgTitle = isDuplicate ? _('Container duplicated') : _('Container created');
						const msgText = isDuplicate ? 
							_('New container duplicated from ') + view.duplicateContainer.Name?.substring(1) : 
							_('New container has been created.');

						if (response?.body?.Warnings) {
							view.showNotification(msgTitle + _(' with warnings'), response?.body?.Warning || msgText, 5000, 'warning');
						} else {
							view.showNotification(msgTitle, msgText, 4000, 'success');
						}
						window.location.href = `${this.dockerman_url}/containers`;
					}
				}
			))
			.catch((err) => {
				view.showNotification(_('Create container failed'), err?.message || String(err), 7000, 'error');
				return false;
			});
	},

	handleSaveApply: null,
	handleReset: null,

});

```

---

# containers.js
```javascript
'use strict';
'require form';
'require fs';
'require poll';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/

/* API v1.52:

GET /containers/{id}/json: the NetworkSettings no longer returns the deprecated
 Bridge, HairpinMode, LinkLocalIPv6Address, LinkLocalIPv6PrefixLen,
 SecondaryIPAddresses, SecondaryIPv6Addresses, EndpointID, Gateway,
 GlobalIPv6Address, GlobalIPv6PrefixLen, IPAddress, IPPrefixLen, IPv6Gateway,
 and MacAddress fields. These fields were deprecated in API v1.21 (docker
 v1.9.0) but kept around for backward compatibility.

*/

return dm2.dv.extend({
	load() {
		return Promise.all([
			dm2.container_list({query: {all: true}}),
			dm2.image_list({query: {all: true}}),
			dm2.network_list({query: {all: true}}),
		]);
	},

	render([containers, images, networks]) {
		if (containers?.code !== 200) {
			return E('div', {}, [ containers?.body?.message ]);
		}

		let container_list = containers.body;
		let network_list = networks.body;
		let image_list = images.body;

		const view = this;
		let containerTable;


		const m = new form.JSONMap({container: view.getContainersTable(container_list, image_list, network_list), prune: {}},
			_('Docker - Containers'),
			_('This page displays all docker Containers that have been created on the connected docker host.') + '<br />' +
			_('Note: docker provides no container import facility.'));
		m.submit = false;
		m.reset = false;

		let s, o;


		let pollPending = null;
		let conSec = null;
		const calculateTotals = () => {
			return {
				running_total: Array.isArray(container_list) ?
					container_list.filter(c => c?.State === 'running').length : 0,
				paused_total: Array.isArray(container_list) ?
					container_list.filter(c => c?.State === 'paused').length : 0,
				stopped_total: Array.isArray(container_list) ?
					container_list.filter(c => ['exited', 'created'].includes(c?.State)).length : 0
			};
		};

		const refresh = () => {
			if (pollPending) return pollPending;
			pollPending = view.load().then(([containers2, images2, networks2]) => {
				image_list = images2.body;
				container_list = containers2.body;
				network_list = networks2.body;
				m.data = new m.data.constructor({ container: view.getContainersTable(container_list, image_list, network_list), prune: {} });

				const totals = calculateTotals();
				if (conSec) {
					conSec.footer = [
						`${_('Total')} ${container_list.length}`,
						[
							`${_('Running')} ${totals.running_total}`,
							E('br'),
							`${_('Paused')} ${totals.paused_total}`,
							E('br'),
							`${_('Stopped')} ${totals.stopped_total}`,
						],
						'',
						'',
					];
				}
				
				return m.render();
			}).catch((err) => { console.warn(err) }).finally(() => { pollPending = null });
			return pollPending;
		};

		s = m.section(form.TableSection, 'prune', _('Containers overview'), null);
		s.addremove = false;
		s.anonymous = true;

		const prune = s.option(form.Button, '_prune', null);
		prune.inputtitle = `${dm2.ActionTypes['prune'].i18n} ${dm2.ActionTypes['prune'].e}`;
		prune.inputstyle = 'negative';
		prune.onclick = L.bind(function(section_id, ev) {
			return this.super('handleXHRTransfer', [{
				q_params: {  },
				commandCPath: '/containers/prune',
				commandDPath: '/containers/prune',
				commandTitle: dm2.ActionTypes['prune'].i18n,
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['prune'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch { }
				},
				noFileUpload: true,
			}]);
		}, this);

		const totals = calculateTotals();
		let running_total = totals.running_total;
		let paused_total = totals.paused_total;
		let stopped_total = totals.stopped_total;

		conSec = m.section(form.TableSection, 'container');
		conSec.anonymous = true;
		conSec.nodescriptions = true;
		conSec.addremove = true;
		conSec.sortable = true;
		conSec.filterrow = true;
		conSec.addbtntitle = `${dm2.ActionTypes['create'].i18n} ${dm2.ActionTypes['create'].e}`;
		conSec.footer = [
			`${_('Total')} ${container_list.length}`,
			[
				`${_('Running')} ${running_total}`,
				E('br'),
				`${_('Paused')} ${paused_total}`,
				E('br'),
				`${_('Stopped')} ${stopped_total}`,
			],
			'',
			'',
		];

		conSec.handleAdd = function(section_id, ev) {
			window.location.href = `${view.dockerman_url}/container_new`;
		};

		conSec.renderRowActions = function(sid) {
			const cont = this.map.data.data[sid];
			return view.buildContainerActions(cont);
		}

		o = conSec.option(form.DummyValue, 'cid', _('Container'));
		o = conSec.option(form.DummyValue, 'State', _('State'));
		o = conSec.option(form.DummyValue, 'Networks', _('Networks'));
		o.rawhtml = true;
		o = conSec.option(form.DummyValue, 'Ports', _('Ports'));
		o.rawhtml = true;
		o = conSec.option(form.DummyValue, 'Command', _('Command'));
		o.width = 200;
		o = conSec.option(form.DummyValue, 'Created', _('Created'));

		poll.add(L.bind(() => { refresh(); }, this), 10);

		this.insertOutputFrame(conSec, m);
		return m.render();

	},

	buildContainerActions(cont, idx) {
		const view = this;
		const isRunning = cont?.State === 'running';
		const isPaused = cont?.State === 'paused';
		const btns = [
			E('button', {
				'class': 'cbi-button view',
				'title': dm2.ActionTypes['inspect'].i18n,
				'click': () => view.executeDockerAction(
					dm2.container_inspect,
					{id: cont.Id},
					dm2.ActionTypes['inspect'].i18n,
					{showOutput: true, showSuccess: false}
				)
			}, [dm2.ActionTypes['inspect'].e]),

			E('button', {
				'class': 'cbi-button cbi-button-positive edit',
				'title': _('Edit this container'),
				'click': () => window.location.href = `${view.dockerman_url}/container/${cont?.Id}`
			}, [dm2.ActionTypes['edit'].e]),

			(() => {
				const icon = isRunning
					? dm2.Types['container'].sub['pause'].e
					: (isPaused 
						? dm2.Types['container'].sub['unpause'].e
						: dm2.Types['container'].sub['start'].e);
				const title = isRunning
					? _('Pause this container')
					: (isPaused ? _('Unpause this container') : _('Start this container'));
				const handler = isRunning
					? () => view.executeDockerAction(
							dm2.container_pause,
							{id: cont.Id},
							dm2.Types['container'].sub['pause'].i18n,
							{showOutput: true, showSuccess: false}
						)
					: (isPaused ? () => view.executeDockerAction(
							dm2.container_unpause,
							{id: cont.Id},
							dm2.Types['container'].sub['unpause'].i18n,
							{showOutput: true, showSuccess: false}
						) : () => view.executeDockerAction(
							dm2.container_start,
							{id: cont.Id},
							dm2.Types['container'].sub['start'].i18n,
							{showOutput: true, showSuccess: false}
						));
				const btnClass = isRunning ? 'cbi-button cbi-button-neutral' : 'cbi-button cbi-button-positive start';

				return E('button', {
					'class': btnClass,
					'title': title,
					'click': handler,
				}, [icon]);
			})(),

			E('button', {
				'class': 'cbi-button cbi-button-neutral restart',
				'title': _('Restart this container'),
				'click': () => view.executeDockerAction(
					dm2.container_restart,
					{id: cont.Id},
					_('Restart'),
					{showOutput: true, showSuccess: false}
				)
			}, [dm2.Types['container'].sub['restart'].e]),

			E('button', {
				'class': 'cbi-button cbi-button-neutral stop',
				'title': _('Stop this container'),
				'click': () => view.executeDockerAction(
					dm2.container_stop,
					{id: cont.Id},
					dm2.Types['container'].sub['stop'].i18n,
					{showOutput: true, showSuccess: false}
				),
				'disabled' : !(isRunning || isPaused) ? true : null
			}, [dm2.Types['container'].sub['stop'].e]),

			E('button', {
				'class': 'cbi-button cbi-button-negative kill',
				'title': _('Kill this container'),
				'click': () => view.executeDockerAction(
					dm2.container_kill,
					{id: cont.Id},
					dm2.Types['container'].sub['kill'].i18n,
					{showOutput: true, showSuccess: false}
				),
				'disabled' : !(isRunning || isPaused) ? true : null
			}, [dm2.Types['container'].sub['kill'].e]),

			E('button', {
				'class': 'cbi-button cbi-button-neutral export',
				'title': _('Export this container'),
				'click': () => {
					window.location.href = `${view.dockerman_url}/container/export/${cont.Id}`;
				}
			}, [dm2.Types['container'].sub['export'].e]),

			E('div', {
				'style': 'width: 20px',
				// Some safety margin for mis-clicks
			}, [' ']),

			E('button', {
				'class': 'cbi-button cbi-button-negative remove',
				'title': dm2.ActionTypes['remove'].i18n,
				'click': () => view.executeDockerAction(
					dm2.container_remove,
					{id: cont.Id, query: { force: false }},
					dm2.ActionTypes['remove'].i18n,
					{showOutput: true, showSuccess: false}
				)
			}, [dm2.ActionTypes['remove'].e]),

			E('button', {
				'class': 'cbi-button cbi-button-negative important remove',
				'title': dm2.ActionTypes['force_remove'].i18n,
				'click': () => view.executeDockerAction(
					dm2.container_remove,
					{id: cont.Id, query: { force: true }},
					_('Force Remove'),
					{showOutput: true, showSuccess: false}
				)
			}, [dm2.ActionTypes['force_remove'].e]),
		];

		return E('td', { 
			'class': 'td',
		}, E('div', btns));
	},

	handleSave: null,
	handleSaveApply: null,
	handleReset: null,

	getContainersTable(containers, image_list, network_list) {
		const data = [];

		for (const cont of Array.isArray(containers) ? containers : []) {

			// build Container ID: xxxxxxx image: xxxx
			const names = Array.isArray(cont?.Names) ? cont.Names : [];
			const cleanedNames = names
				.map(n => (typeof n === 'string' ? n.substring(1) : ''))
				.filter(Boolean)
				.join(', ');
			const statusColorName = this.wrapStatusText(cleanedNames, cont.State, 'font-weight:600;');
			const imageName = this.getImageFirstTag(image_list, cont.ImageID);
			const shortId = (cont?.Id || '').substring(0, 12);

			const cid = E('div', {}, [
					E('a', { href: `container/${cont.Id}`, title: dm2.ActionTypes['edit'].i18n }, [
						statusColorName,
						E('div', { 'style': 'font-size: 0.9em; font-family: monospace; ' }, [`ID: ${shortId}`]),
					]),
				E('div', { 'style': 'font-size: 0.85em;' }, [`${dm2.Types['image'].i18n}: ${imageName}`]),
			])

			// Just push plain data objects without UCI metadata
			data.push({
				...cont,
				cid: cid,
				_shortId: (cont?.Id || '').substring(0, 12),
				Networks: this.parseNetworkLinksForContainer(network_list, cont?.NetworkSettings?.Networks || {}, true),
				Created: this.buildTimeString(cont?.Created) || '',
				Ports: (Array.isArray(cont.Ports) && cont.Ports.length > 0)
						? cont.Ports.map(p => {
							// const ip = p.IP || '';
							const pub = p.PublicPort || '';
							const priv = p.PrivatePort || '';
							const type = p.Type || '';
							return `${pub ? pub + ':' : ''}${priv}/${type}`;
							// return `${ip ? ip + ':' : ''}${pub} -> ${priv} (${type})`;
						}).join('<br/>')
						: '',
			});
		}

		return data;
	},

});

```

---

# events.js
```javascript
'use strict';
'require form';
'require fs';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
LICENSE: GPLv2.0
*/


/* API v1.52

GET /events supports content-type negotiation and can produce either
 application/x-ndjson (Newline delimited JSON object stream) or
 application/json-seq (RFC7464).

application/x-ndjson:

{"some":"thing\n"}
{"some2":"thing2\n"}
...

application/json-seq: ␊ = \n | ^J | 0xa, ␞ = ␞ | ^^ | 0x1e

␞{"some":"thing\n"}␊
␞{"some2":"thing2\n"}␊
...

*/

return dm2.dv.extend({
	load() {
		const now = Math.floor(Date.now() / 1000);
		this.js_api = false;

		return Promise.all([
			dm2.docker_events({ query: { since: `0`, until: `${now}` } }),
			dm2.js_api_ready.then(([ok, ]) => this.js_api = ok),
		]);
	},

	render([events, js_api_available]) {
		if (events?.code !== 200) {
			return E('div', {}, [ events?.body?.message ]);
		}

		this.outputText = events?.body ? JSON.stringify(events?.body, null, 2) + '\n' : '';
		const event_list = events?.body || [];
		const view = this;

		const mainContainer = E('div', { 'class': 'cbi-map' }, [
			E('h2', {}, [_('Docker - Events')])
		]);

		// Filters
		const now = new Date();
		const nowIso = now.toISOString().slice(0, 16);
		const filtersSection = E('div', { 'class': 'cbi-section' }, [
			E('div', { 'class': 'cbi-section-node' }, [
				E('div', { 'class': 'cbi-value' }, [
					E('label', { 'class': 'cbi-value-title' }, _('Type')),
					E('div', { 'class': 'cbi-value-field' }, [
						E('select', {
							'id': 'event-type-filter',
							'class': 'cbi-input-select',
							'change': () => {
								view.updateSubtypeFilter(this.value);
								view.renderEventsTable(event_list);
							}
						}, [
							E('option', { 'value': '' }, _('All Types')),
							...Object.keys(dm2.Types).map(type => 
								E('option', { 'value': type }, `${dm2.Types[type].e} ${dm2.Types[type].i18n}`)
							)
						])
					])
				]),
				E('div', { 'class': 'cbi-value' }, [
					E('label', { 'class': 'cbi-value-title' }, _('Subtype')),
					E('div', { 'class': 'cbi-value-field' }, [
						E('select', {
							'id': 'event-subtype-filter',
							'class': 'cbi-input-select',
							'disabled': true,
							'change': () => {
								view.renderEventsTable(event_list);
							}
						}, [
							E('option', { 'value': '' }, _('Select Type First'))
						])
					])
				]),
				E('div', { 'class': 'cbi-value' }, [
					E('label', { 'class': 'cbi-value-title' }, _('From')),
					E('div', { 'class': 'cbi-value-field' }, [
						E('input', {
							'id': 'event-from-date',
							'type': 'datetime-local',
							'value': '1970-01-01T00:00',
							'step': 60,
							'style': 'width: 180px;',
							'change': () => { view.renderEventsTable(event_list); }
						}),
						E('button', {
							'type': 'button',
							'class': 'cbi-button',
							'style': 'margin-left: 8px;',
							'click': () => {
								const now = new Date();
								const iso = now.toISOString().slice(0,16);
								document.getElementById('event-from-date').value = iso;
								view.renderEventsTable(event_list);
							}
						}, _('Now')),
						E('button', {
							'type': 'button',
							'class': 'cbi-button',
							'style': 'margin-left: 8px;',
							'click': () => {
								const unixzero = new Date(0);
								const iso = unixzero.toISOString().slice(0,16);
								document.getElementById('event-from-date').value = iso;
								view.renderEventsTable(event_list);
							}
						}, _('0'))
					])
				]),
				E('div', { 'class': 'cbi-value' }, [
					E('label', { 'class': 'cbi-value-title' }, _('To')),
					E('div', { 'class': 'cbi-value-field' }, [
						E('input', {
							'id': 'event-to-date',
							'type': 'datetime-local',
							'value': nowIso,
							'step': 60,
							'style': 'width: 180px;',
							'change': () => { view.renderEventsTable(event_list); }
						}),
						E('button', {
							'type': 'button',
							'class': 'cbi-button',
							'style': 'margin-left: 8px;',
							'click': () => {
								const now = new Date();
								const iso = now.toISOString().slice(0,16);
								document.getElementById('event-to-date').value = iso;
								view.renderEventsTable(event_list);
							}
						}, _('Now'))
					])
				])
			])
		]);
		mainContainer.appendChild(filtersSection);

		this.tableSection = E('div', { 'class': 'cbi-section', 'id': 'events-section' });
		mainContainer.appendChild(this.tableSection);

		this.renderEventsTable(event_list);

		mainContainer.appendChild(this.insertOutputFrame(E('div', {}), null));

		return mainContainer;
	},

	renderEventsTable(event_list) {
		const view = this;

		// Get filter values
		const typeFilter = document.getElementById('event-type-filter')?.value || '';
		const subtypeFilter = document.getElementById('event-subtype-filter')?.value || '';

		// Build filters object for docker_events API
		const filters = {};
		if (typeFilter) {
			filters.type = [typeFilter];
		}
		if (subtypeFilter) {
			filters.event = [subtypeFilter];
		}

		// Show loading indicator
		this.tableSection.innerHTML = '';

		// Query docker events with filters and date range
		const fromInput = document.getElementById('event-from-date');
		const toInput = document.getElementById('event-to-date');
		let since = '0';
		let until = Math.floor(Date.now() / 1000).toString();
		if (fromInput && fromInput.value) {
			const fromDate = new Date(fromInput.value);
			if (!isNaN(fromDate.getTime())) {
				since = Math.floor(fromDate.getTime() / 1000).toString();
				since = since < 0 ? 0 : since;
			}
		}
		if (toInput && toInput.value) {
			const toDate = new Date(toInput.value);
			if (!isNaN(toDate.getTime())) {
				const now = Date.now() / 1000;
				until = Math.floor(toDate.getTime() / 1000).toString();
				until = !this.js_api ? until > now ? now : until : until;
			}
		}
		const queryParams = { since, until };
		if (Object.keys(filters).length > 0) {
			// docker pre v27: filters => docker *streams* events. v27, send events in body.
			// Some older dockerd endpoints don't like encoded filter params, even if we can't stream.
			queryParams.filters = JSON.stringify(filters);
		}

		event_list = new Set();
		view.outputText = '';
		let eventsTable = null;
		// Batching for speed
		let batchBuffer = new Set();
		let batchTimer = null;
		const BATCH_SIZE = 256;
		const BATCH_INTERVAL = 500; // ms

		function updateTable() {
			const ev_array = Array.from(event_list.keys());
			const rows = ev_array.map(event => {
				const type = event.Type;
				const typeInfo = dm2.Types[type];
				const typeDisplay = typeInfo ? `${typeInfo.e} ${typeInfo.i18n}` : type;
				const actionParts = event.Action?.split(':') || [];
				const action = actionParts.length > 0 ? actionParts[0] : '';
				const action_sub = actionParts.length > 1 ? actionParts[1] : null;
				const actionInfo = typeInfo?.sub?.[action];
				const actionDisplay = actionInfo ? `${actionInfo.e} ${actionInfo.i18n}${action_sub ? ':'+action_sub : ''}` : action;
				return [
					view.buildTimeString(event.time),
					typeDisplay,
					actionDisplay,
					view.objectToText(event.Actor),
					event.scope || ''
				];
			});

			const output = JSON.stringify(ev_array, null, 2);
			view.outputText = output + '\n';
			view.insertOutput(view.outputText);

			if (!eventsTable) {
				eventsTable = new L.ui.Table(
					[_('Time'), _('Type'), _('Action'), _('Actor'), _('Scope')],
					{ id: 'events-table', style: 'width: 100%; table-layout: auto;' },
					E('em', [_('No events found')])
				);
				view.tableSection.innerHTML = '';
				view.tableSection.appendChild(eventsTable.render());
			}
			eventsTable.update(rows);
		}

		view.tableSection.innerHTML = '';

		function flushBatch() {
			if (batchBuffer.size) {
				batchBuffer = new Set();
			}
			if (batchTimer) {
				clearTimeout(batchTimer);
				batchTimer = null;
			}
			updateTable();
		}

		function handleEventChunk(event) {
			event_list.add(event);
			batchBuffer.add(event);
			if (batchBuffer.size >= BATCH_SIZE) {
				flushBatch();
			} else if (!batchTimer) {
				batchTimer = setTimeout(flushBatch, BATCH_INTERVAL);
			}
		}

		/* Partial transfers work but XHR times out waiting, even with xhr.timeout = 0 */
		// view.handleXHRTransfer({
		// 	q_params:{ query: queryParams },
		// 	commandCPath: '/docker/events',
		// 	commandDPath: '/events',
		// 	commandTitle: dm2.ActionTypes['prune'].i18n,
		// 	showProgress: false,
		// 	onUpdate: (msg) => {
		// 		try {
		// 			if(msg.error)
		// 				ui.addTimeLimitedNotification(dm2.ActionTypes['prune'].i18n, msg.error, 7000, 'error');

		// 			event_list.add(msg);
		// 			updateTable();

		// 			const output = JSON.stringify(msg, null, 2) + '\n';
		// 			view.insertOutput(output);
		// 		} catch {

		// 		}
		// 	},
		// 	noFileUpload: true,
		// });

		view.executeDockerAction(
			dm2.docker_events,
			{ query: queryParams, onChunk: handleEventChunk },
			_('Load Events'),
			{
				showOutput: false,
				showSuccess: false,
				onSuccess: (response) => {
					if (response.body)
						event_list = Array.isArray(response.body) ? new Set(response.body) : new Set([response.body]);
					updateTable();
					flushBatch();
				},
				onError: (err) => {
					view.tableSection.innerHTML = '';
					view.tableSection.appendChild(E('em', { 'style': 'color: red;' }, _('Failed to load events: %s').format(err?.message || err)));
				}
			}
		);
	},

	updateSubtypeFilter(selectedType) {
		const subtypeSelect = document.getElementById('event-subtype-filter');
		if (!subtypeSelect) return;

		// Clear existing options
		subtypeSelect.innerHTML = '';

		if (!selectedType || !dm2.Types[selectedType] || !dm2.Types[selectedType].sub) {
			subtypeSelect.disabled = true;
			subtypeSelect.appendChild(E('option', { 'value': '' }, _('Select Type First')));
			return;
		}

		// Enable and populate with subtypes
		subtypeSelect.disabled = false;
		subtypeSelect.appendChild(E('option', { 'value': '' }, _('All Subtypes')));

		const subtypes = dm2.Types[selectedType].sub;
		for (const action in subtypes) {
			subtypeSelect.appendChild(
				E('option', { 'value': action }, `${subtypes[action].e} ${subtypes[action].i18n}`)
			);
		}
	},

	handleSave: null,
	handleSaveApply: null,
	handleReset: null,

});

```

---

# images.js
```javascript
'use strict';
'require form';
'require fs';
'require poll';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/


return dm2.dv.extend({
	load() {
		return Promise.all([
			dm2.image_list(),
			dm2.container_list({query: {all: true}}),
		])
	},

	render([images, containers]) {
		if (images?.code !== 200) {
			return E('div', {}, [ images.body.message ]);
		}

		let image_list = this.getImagesTable(images.body);
		let container_list = containers.body;
		const view = this; // Capture the view context
		view.selectedImages = {};

		let s, o;
		const m = new form.JSONMap({image: image_list, pull: {}, push: {}, build: {}, import: {}, prune: {}},
			_('Docker - Images'),
			_('On this page all images are displayed that are available on the system and with which a container can be created.'));
		m.submit = false;
		m.reset = false;

		let pollPending = null;
		let imgSec = null;
		const calculateSizeTotal = () => {
			return Array.isArray(image_list) ? image_list.map(c => c?.Size).reduce((acc, e) => acc + e, 0) : 0;
		};

		const refresh = () => {
			if (pollPending) return pollPending;
			pollPending = view.load().then(([images2, containers2]) => {
				image_list = view.getImagesTable(images2.body);
				container_list = containers2.body;
				m.data = new m.data.constructor({ image: image_list, pull: {}, push: {}, build: {}, import: {}, prune: {} });

				const size_total = calculateSizeTotal();
				if (imgSec) {
					imgSec.footer = [
						'',
						`${_('Total')} ${image_list.length}`,
						'',
						`${'%1024mB'.format(size_total)}`,
					];
				}

				return m.render();
			}).catch((err) => { console.warn(err) }).finally(() => { pollPending = null });
			return pollPending;
		};

		// Pull image

		s = m.section(form.TableSection, 'pull',  dm2.Types['image'].sub['pull'].i18n,
			_('By entering a valid image name with the corresponding version, the docker image can be downloaded from the configured registry.'));
		s.anonymous = true;
		s.addremove = false;

		const splitImageTag = (value) => {
			const input = String(value || '').trim();
			if (!input || input.includes(' ')) return { name: '', tag: 'latest' };

			const lastSlash = input.lastIndexOf('/');
			const lastColon = input.lastIndexOf(':');
			if (lastColon > lastSlash) {
				return {
					name: input.slice(0, lastColon) || input,
					tag: input.slice(lastColon + 1) || 'latest'
				};
			}

			return { name: input, tag: 'latest' };
		};

		let tagOpt = s.option(form.Value, '_image_tag_name');
		tagOpt.placeholder = "[registry.io[:443]/]foobar/product:latest";

		o = s.option(form.Button, '_pull');
		o.inputtitle = `${dm2.Types['image'].sub['pull'].i18n} ${dm2.Types['image'].sub['pull'].e}`; // _('Pull') + ' ☁️⬇️'
		o.inputstyle = 'add';
		o.onclick = L.bind(function(ev, btn) {
			const raw = tagOpt.formvalue('pull') || '';
			const input = String(raw).trim();
			if (!input) {
				ui.addTimeLimitedNotification(dm2.Types['image'].sub['pull'].i18n, _('Please enter an image tag'), 4000, 'warning');
				return false;
			}

			const { name, tag: ver } = splitImageTag(input);

			return this.super('handleXHRTransfer', [{
				q_params: { query: { fromImage: name, tag: ver } },
				commandCPath: `/images/create`,
				commandDPath: `/images/create`,
				commandTitle: dm2.Types['image'].sub['pull'].i18n,
				successMessage: _('Image create completed'),
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['build'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				onSuccess: () => refresh(),
				noFileUpload: true,
			}]);

			// return view.executeDockerAction(
			// 	dm2.image_create,
			// 	{ query: { fromImage: name, tag: ver } },
			// 	dm2.Types['image'].sub['pull'].i18n,
			// 	{
			// 		showOutput: true,
			// 		successMessage: _('Image create completed')
			// 	}
			// );
		}, this);

		// Push image

		s = m.section(form.TableSection, 'push',  dm2.Types['image'].sub['push'].i18n,
			_('Push an image to a registry. Select an image tag from all available tags on the system.'));
		s.anonymous = true;
		s.addremove = false;

		// Build a list of all available tags across all images
		const allImageTags = [];
		for (const image of image_list) {
			const tags = Array.isArray(image.RepoTags) ? image.RepoTags : [];
			for (const tag of tags) {
				if (tag && tag !== '<none>:<none>') {
					allImageTags.push(tag);
				}
			}
		}

		let pushTagOpt = s.option(form.Value, '_image_tag_push');
		pushTagOpt.placeholder = _('Select image tag');
		if (allImageTags.length === 0) {
			pushTagOpt.value('', _('No image tags available'));
		} else {
			// Add all unique tags to the dropdown
			const uniqueTags = [...new Set(allImageTags)].sort();
			for (const tag of uniqueTags) {
				pushTagOpt.value(tag, tag);
			}
		}

		o = s.option(form.Button, '_push');
		o.inputtitle = `${dm2.Types['image'].sub['push'].i18n} ${dm2.Types['image'].sub['push'].e}`; // _('Push') + ' ☁️⬆️'
		o.inputstyle = 'add';
		o.onclick = L.bind(function(ev, btn) {
			const selected = pushTagOpt.formvalue('push') || '';
			if (!selected) {
				ui.addTimeLimitedNotification(dm2.Types['image'].sub['push'].i18n, _('Please select an image tag to push'), 4000, 'warning');
				return false;
			}

			const { name, tag: ver } = splitImageTag(selected);

			return this.super('handleXHRTransfer', [{
				// Pass name in q_params to trigger building X-Registry-Auth header
				q_params: { name: name, query: { tag: ver } },
				commandCPath: `/images/push/${name}`,
				commandDPath: `/images/${name}/push`,
				commandTitle: dm2.Types['image'].sub['push'].i18n,
				successMessage: _('Image push completed'),
				onSuccess: () => refresh(),
				noFileUpload: true,
			}]);

			// return view.executeDockerAction(
			// 	dm2.image_push,
			// 	{ name: name, query: { tag: ver} },
			// 	dm2.Types['image'].sub['push'].i18n,
			// 	{
			// 		showOutput: true,
			// 		successMessage: _('Image push completed')
			// 	}
			// );
		}, this);


		s = m.section(form.TableSection, 'build',  dm2.ActionTypes['build'].i18n,
			_('Build an image.') + ' ' + _('git repositories require git installed on the docker host.'));
		s.anonymous = true;
		s.addremove = false;

		let buildOpt = s.option(form.Value, '_image_build_uri');
		buildOpt.placeholder = "https://host/foo/bar.git | https://host/foobar.tar";

		let buildTagOpt = s.option(form.Value, '_image_build_tag');
		buildTagOpt.placeholder = 'repository:tag';

		o = s.option(form.Button, '_build');
		o.inputtitle = `${dm2.ActionTypes['build'].i18n} ${dm2.ActionTypes['build'].e}`; // _('Build') + ' 🏗️'
		o.inputstyle = 'add';
		o.onclick = L.bind(function(ev, btn) {
			const uri = buildOpt.formvalue('build') || '';
			const t = buildTagOpt.formvalue('build') || '';

			const q_params = { q: encodeURIComponent('false'), t: t };
			if (uri) q_params.remote = encodeURIComponent(uri);

			return this.super('handleXHRTransfer', [{
				q_params: { query: q_params },
				commandCPath: '/images/build',
				commandDPath: '/build',
				commandTitle: dm2.ActionTypes['build'].i18n,
				successMessage: _('Image loaded successfully'),
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['build'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				onSuccess: () => refresh(),
				noFileUpload: !!uri,
			}]);
		}, this);

		o = s.option(form.Button, '_delete_cache', null);
		o.inputtitle = `${dm2.ActionTypes['clean'].i18n} ${dm2.ActionTypes['clean'].e}`;
		o.inputstyle = 'negative';
		o.onclick = L.bind(function(ev, btn) {
			return this.super('handleXHRTransfer', [{
				q_params: { query: { all: 'true' } },
				commandCPath: '/images/build/prune',
				commandDPath: '/build/prune',
				commandTitle: dm2.Types['builder'].sub['prune'].i18n,
				successMessage: _('Cleaned build cache'),
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['clean'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				noFileUpload: true,
			}]);
		}, this);

		// Import image

		s = m.section(form.TableSection, 'import', dm2.Types['image'].sub['import'].i18n,
			_('Download a valid remote image tar.'));
		s.addremove = false;
		s.anonymous = true;

		let imgsrc = s.option(form.Value, '_image_source');
		imgsrc.placeholder = 'https://host/image.tar';

		let tagimpOpt = s.option(form.Value, '_import_image_tag_name');
		tagimpOpt.placeholder = 'repository:tag';

		let importBtn = s.option(form.Button, '_import');
		importBtn.inputtitle = `${dm2.Types['image'].sub['import'].i18n} ${dm2.Types['image'].sub['import'].e}` //_('Import') + ' ➡️';
		importBtn.inputstyle = 'add';
		importBtn.onclick = L.bind(function(ev, btn) {
			const rawtag = tagimpOpt.formvalue('import') || '';
			const input = String(rawtag).trim();
			if (!input) {
				ui.addTimeLimitedNotification(dm2.Types['image'].sub['import'].i18n, _('Please enter an image repo tag'), 4000, 'warning');
				return false;
			}
			const rawremote = imgsrc.formvalue('import') || '';
			let remote = String(rawremote).trim();
			if (!remote) {
				ui.addTimeLimitedNotification(dm2.Types['image'].sub['import'].i18n, _('Please enter an image source'), 4000, 'warning');
				return false;
			}

			const { name, tag: ver } = splitImageTag(input);

			return this.super('handleXHRTransfer', [{
				q_params: { query: { fromSrc: remote, repo: ver } },
				commandCPath: '/images/create',
				commandDPath: '/images/create',
				commandTitle: dm2.Types['image'].sub['create'].i18n,
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.Types['image'].sub['create'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				onSuccess: () => refresh(),
				noFileUpload: true,
			}]);

			// return view.executeDockerAction(
			// 	dm2.image_create,
			// 	{ query: { fromSrc: remote, repo: ver } },
			// 	dm2.Types['image'].sub['import'].i18n,
			// 	{
			// 		showOutput: true,
			// 		successMessage: _('Image create started/completed')
			// 	}
			// );
		}, this);


		s = m.section(form.TableSection, 'prune', _('Images overview'), );
		s.addremove = false;
		s.anonymous = true;

		const prune = s.option(form.Button, '_prune', null);
		prune.inputtitle = `${dm2.ActionTypes['prune'].i18n} ${dm2.ActionTypes['prune'].e}`;
		prune.inputstyle = 'negative';
		prune.onclick = L.bind(function(ev, btn) {

			return this.super('handleXHRTransfer', [{
				q_params: {  },
				commandCPath: '/images/prune',
				commandDPath: '/images/prune',
				commandTitle: dm2.ActionTypes['prune'].i18n,
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['prune'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				onSuccess: () => refresh(),
				noFileUpload: true,
			}]);

			// return view.executeDockerAction(
			// 	dm2.image_prune,
			// 	{ query: { filters: '' } },
			// 	dm2.ActionTypes['prune'].i18n,
			// 	{
			// 		showOutput: true,
			// 		successMessage: _('started/completed'),
			//		onSuccess: () => refresh(),
			// 	}
			// );
		}, this);

		o = s.option(form.Button, '_export', null);
		o.inputtitle = `${dm2.ActionTypes['save'].i18n} ${dm2.ActionTypes['save'].e}`;
		o.inputstyle = 'cbi-button-positive';
		o.onclick = L.bind(function(ev, btn) {
			ev.preventDefault();

			const selected = Object.keys(view.selectedImages).filter(k => view.selectedImages[k]);
			if (!selected.length) {
				ui.addTimeLimitedNotification(_('Export'), _('No images selected'), 3000, 'warning');
				return;
			}

			// Get tags or IDs for selected images
			const names = selected.map(sid => {
				const image = s.map.data.data[sid];
				const tag = image?.RepoTags?.[0];
				return tag || image?.Id?.substr(12);
			});

			// http.uc does not yet handle parameter arrays, so /images/get needs access to the URL params
			window.location.href = `${view.dockerman_url}/images/get?${names.map(e => `names=${e}`).join('&')}`;

		}, this);

		const size_total = calculateSizeTotal();

		imgSec = m.section(form.TableSection, 'image');
		imgSec.anonymous = true;
		imgSec.nodescriptions = true;
		imgSec.addremove = true;
		imgSec.sortable = true;
		imgSec.filterrow = true;
		imgSec.addbtntitle = `${dm2.ActionTypes['upload'].i18n} ${dm2.ActionTypes['upload'].e}`;
		imgSec.footer = [
			'',
			`${_('Total')} ${image_list.length}`,
			'',
			`${'%1024mB'.format(size_total)}`,
		];

		imgSec.handleAdd = function(sid, ev) {
			return view.handleFileUpload();
		};

		imgSec.handleGet = function(image, ev) {
			const tag = image.RepoTags?.[0];
			const name = tag || image.Id.substr(12);

			// Direct HTTP download - avoid RPC
			window.location.href = `${view.dockerman_url}/images/get/${name}`;
			return true;
		};

		imgSec.handleRemove = function(sid, image, force=false, ev) {
			return view.executeDockerAction(
				dm2.image_remove,
				{ id: image.Id, query: { force: force } },
				dm2.ActionTypes['remove'].i18n,
				{
					showOutput: true,
					onSuccess: () => {
						delete this.map.data.data[sid];
						return this.super('handleRemove', [ev]);
					}
				}
			);
		};

		imgSec.handleInspect = function(image, ev) {
			return view.executeDockerAction(
				dm2.image_inspect,
				{ id: image.Id },
				dm2.ActionTypes['inspect'].i18n,
				{ showOutput: true, showSuccess: false }
			);
		};

		imgSec.handleHistory = function(image, ev) {
			return view.executeDockerAction(
				dm2.image_history,
				{ id: image.Id },
				dm2.ActionTypes['history'].i18n,
				{ showOutput: true, showSuccess: false }
			);
		};

		imgSec.renderRowActions = function (sid) {
			const image = this.map.data.data[sid];
			const btns = [
				E('button', {
					'class': 'cbi-button cbi-button-neutral',
					'title': dm2.ActionTypes['inspect'].i18n,
					'click': ui.createHandlerFn(this, this.handleInspect, image),
				}, [dm2.ActionTypes['inspect'].e]),
				E('button', {
					'class': 'cbi-button cbi-button-neutral',
					'title': dm2.ActionTypes['history'].i18n,
					'click': ui.createHandlerFn(this, this.handleHistory, image),
				}, [dm2.ActionTypes['history'].e]),
				E('button', {
					'class': 'cbi-button cbi-button-positive save',
					'title': dm2.ActionTypes['save'].i18n,
					'click': ui.createHandlerFn(this, this.handleGet, image),
				}, [dm2.ActionTypes['save'].e]),
				E('div', {
					'style': 'width: 20px',
					// Some safety margin for mis-clicks
				}, [' ']),
				E('button', {
					'class': 'cbi-button cbi-button-negative remove',
					'title': dm2.ActionTypes['remove'].i18n,
					'click': ui.createHandlerFn(this, this.handleRemove, sid, image, false),
					'disabled': image?._disable_delete,
				}, [dm2.ActionTypes['remove'].e]),
				E('button', {
					'class': 'cbi-button cbi-button-negative important remove',
					'title': dm2.ActionTypes['force_remove'].i18n,
					'click': ui.createHandlerFn(this, this.handleRemove, sid, image, true),
					'disabled': image?._disable_delete,
				}, [dm2.ActionTypes['force_remove'].e]),
			];
			return E('td', { 'class': 'td middle cbi-section-actions' }, E('div', btns));
		};

		o = imgSec.option(form.Flag, '_selected');
		o.onchange = function(ev, sid, value) {
			if (value == 1) {
				view.selectedImages[sid] = value;
			}
			else {
				delete view.selectedImages[sid];
			}
			return;
		}

		o = imgSec.option(form.DummyValue, 'RepoTags', dm2.Types['image'].sub['tag'].e);
		o.cfgvalue = function(sid) {
			const image = this.map.data.data[sid];
			const tags = Array.isArray(image?.RepoTags) ? image.RepoTags : [];

			if (tags.length === 0 || (tags.length === 1 && tags[0] === '<none>:<none>'))
				return '<none>';

			const tagLinks = tags.map(tag => {
				if (tag === '<none>:<none>')
					return E('span', {}, tag);

				/* last tag - don't link it - last tag removal == delete */
				if (tags.length === 1)
					return tag;

				return E('a', {
					'href': '#',
					'title': _('Click to remove this tag'),
					'click': ui.createHandlerFn(view, (tag, imageId, ev) => {

						ev.preventDefault();
						ui.showModal(_('Remove tag'), [
							E('p', {}, _('Do you want to remove the tag "%s"?').format(tag)),
							E('div', { 'class': 'right' }, [
								E('button', {
									'class': 'cbi-button',
									'click': ui.hideModal
								}, '↩'),
								' ',
								E('button', {
									'class': 'cbi-button cbi-button-negative',
									'click': ui.createHandlerFn(view, () => {
										ui.hideModal();

										return view.executeDockerAction(
											dm2.image_remove,
											{ id: tag, query: { noprune: 'true' } },
											dm2.Types['image'].sub['untag'].i18n,
											{
												showOutput: true,
												successMessage: _('Tag removed successfully'),
												successDuration: 4000,
												onSuccess: () => refresh(),
											}
										);
									})
								}, dm2.Types['image'].sub['untag'].e)
							])
						]);
					}, tag, image.Id)
				}, tag);
			});

			// Join with commas and spaces
			const content = [];
			for (const [i, tag] of tagLinks.entries()) {
				if (i > 0) content.push(', ');
				content.push(tag);
			}

			return E('span', {}, content);
		};

		o = imgSec.option(form.DummyValue, 'Containers', _('Containers'));
		o.cfgvalue = function(sid) {
			const imageId = this.map.data.data[sid].Id;
			// Collect all matching container name links for this image
			const anchors = container_list.reduce((acc, container) => {
				if (container?.ImageID !== imageId) return acc;
				for (const name of container?.Names || [])
					acc.push(E('a', { href: `container/${container.Id}` }, [ name.substring(1) ]));
				return acc;
			}, []);

			// Interleave separators
			if (!anchors.length) return E('div', {});
			const content = [];
			for (let i = 0; i < anchors.length; i++) {
				if (i) content.push(' | ');
				content.push(anchors[i]);
			}

			return E('div', {}, content);
		};

		o = imgSec.option(form.DummyValue, 'Size', _('Size'));
		o.cfgvalue = function(sid) {
			const s = this.map.data.data[sid].Size;
			return '%1024mB'.format(s);
		};
		imgSec.option(form.DummyValue, 'Created', _('Created'));
		o = imgSec.option(form.DummyValue, '_id', _('ID'));

		/* Remember: we load a JSONMap - so uci config is non-existent for these
		elements, so we must pull from this.map.data, otherwise o.load returns nothing */
		o.cfgvalue = function(sid) {
			const image = this.map.data.data[sid];
			const shortId = image?._id || '';
			const fullId = image?.Id || '';

			return E('a', {
				'href': '#',
				'style': 'font-family: monospace',
				'title': _('Click to add a new tag to this image'),
				'click': ui.createHandlerFn(view, function(imageId, ev) {
					ev.preventDefault();

					let repoInput, tagInput;
					ui.showModal(_('New tag'), [
						E('p', {}, _('Enter a new tag for image %s:').format(imageId.slice(7, 19))),
						E('div', { 'class': 'cbi-value' }, [
							E('label', { 'class': 'cbi-value-title' }, _('Repository')),
							E('div', { 'class': 'cbi-value-field' }, [
								repoInput = E('input', {
									'type': 'text',
									'class': 'cbi-input-text',
									'placeholder': '[registry.io[:443]/]myrepo/myimage'
								})
							])
						]),
						E('div', { 'class': 'cbi-value' }, [
							E('label', { 'class': 'cbi-value-title' }, _('Tag')),
							E('div', { 'class': 'cbi-value-field' }, [
								tagInput = E('input', {
									'type': 'text',
									'class': 'cbi-input-text',
									'placeholder': 'latest',
									'value': 'latest'
								})
							])
						]),
						E('div', { 'class': 'right' }, [
							E('button', {
								'class': 'cbi-button',
								'click': ui.hideModal
							}, ['↩']),
							' ',
							E('button', {
								'class': 'cbi-button cbi-button-positive',
								'click': ui.createHandlerFn(view, () => {
									const repo = repoInput.value.trim();
									const tag = tagInput.value.trim() || 'latest';

									if (!repo) {
										ui.addTimeLimitedNotification(null, [_('Repository cannot be empty')], 3000, 'warning');
										return;
									}

									ui.hideModal();

									return view.executeDockerAction(
										dm2.image_tag,
										{ id: imageId, query: { repo: repo, tag: tag } },
										dm2.Types['image'].sub['tag'].i18n,
										{
											showOutput: true,
											successMessage: _('Tag added successfully'),
											successDuration: 4000,
											onSuccess: () => refresh(),
										}
									);
								})
							}, [dm2.Types['image'].sub['tag'].e])
						])
					]);
				}, fullId)
			}, shortId);
		};

		this.insertOutputFrame(s, m);

		poll.add(L.bind(() => { refresh(); }, this), 10);

		return m.render();
	},

	handleFileUpload() {
		// const uploadUrl = `?quiet=${encodeURIComponent('false')}`;

		return this.super('handleXHRTransfer', [{
			q_params: { query: { quiet: 'false' } },
			commandCPath: `/images/load`,
			commandDPath: `/images/load`,
			commandTitle: _('Uploading…'),
			commandMessage: _('Uploading image…'),
			successMessage: _('Image loaded successfully'),
			defaultPath: '/tmp'
		}]);
	},

	handleSave: null,
	handleSaveApply: null,
	handleReset: null,

	getImagesTable(images) {
		const data = [];

		for (const image of images) {
			// Just push plain data objects without UCI metadata
			data.push({
				...image,
				_disable_delete: null,
				_id: (image.Id || '').substring(7, 20),
				Created: this.buildTimeString(image.Created) || '',
			});
		}

		return data;
	},

});

```

---

# network.js
```javascript
'use strict';
'require form';
'require fs';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/


return dm2.dv.extend({
	load() {
		const requestPath = L.env.requestpath;
		const netId = requestPath[requestPath.length-1] || '';
		this.networkId = netId;

		return Promise.all([
			dm2.network_inspect({ id: netId }),
			dm2.container_list({query: {all: true}}),
		]);
	},

	render([network, containers]) {
		if (network?.code !== 200) {
			window.location.href = `${this.dockerman_url}/networks`;
			return;
		}

		const view = this;
		const this_network = network.body || {};
		const container_list = Array.isArray(containers.body) ? containers.body : [];

		const m = new form.JSONMap({
				network: this_network,
				Driver: this_network?.IPAM?.Driver,
				Config: this_network?.IPAM?.Config,
				Containers: Object.entries(this_network?.Containers || {}).map(([id, info]) => ({ id, ...info })),
				_inspect: {},
			},
			_('Docker - Networks'),
			_('This page displays all docker networks that have been created on the connected docker host.'));
		m.submit = false;
		m.reset = false;

		let s = m.section(form.NamedSection, 'network', _('Networks overview'));
		s.anonymous = true;
		s.addremove = false;
		s.nodescriptions = true;

		let o, ss;

		// INFO TAB
		s.tab('info', _('Info'));

		o = s.taboption('info', form.DummyValue, 'Name', _('Network Name'));
		o = s.taboption('info', form.DummyValue, 'Id', _('ID'));
		o = s.taboption('info', form.DummyValue, 'Created', _('Created'));
		o = s.taboption('info', form.DummyValue, 'Scope', _('Scope'));
		o = s.taboption('info', form.DummyValue, 'Driver', _('Driver'));
		o = s.taboption('info', form.Flag, 'EnableIPv6', _('IPv6'));
		o.readonly = true;

		o = s.taboption('info', form.Flag, 'Internal', _('Internal'));
		o.readonly = true;

		o = s.taboption('info', form.Flag, 'Attachable', _('Attachable'));
		o.readonly = true;

		o = s.taboption('info', form.Flag, 'Ingress', _('Ingress'));
		o.readonly = true;

		o = s.taboption('info', form.DummyValue, 'ConfigFrom', _('ConfigFrom'));
		o.cfgvalue = view.objectCfgValueTT;


		o = s.taboption('info', form.Flag, 'ConfigOnly', _('Config Only'));
		o.readonly = true;
		o.cfgvalue = view.objectCfgValueTT;

		o = s.taboption('info', form.DummyValue, 'Containers', _('Containers'));
		o.load = function(sid) {
			return view.parseContainerLinksForNetwork(this_network, container_list);
		};

		o = s.taboption('info', form.DummyValue, 'Options', _('Options'));
		o.cfgvalue = view.objectCfgValueTT;

		o = s.taboption('info', form.DummyValue, 'Labels', _('Labels'));
		o.cfgvalue = view.objectCfgValueTT;

		// CONFIGS TAB
		s.tab('detail', _('Detail'));

		o = s.taboption('detail', form.DummyValue, 'Driver', _('IPAM Driver'));

		o = s.taboption('detail', form.SectionValue, '_conf_', form.TableSection, 'Config', _('Network Configurations'));
		ss = o.subsection;
		ss.anonymous = true;

		ss.option(form.DummyValue, 'Subnet', _('Subnet'));
		ss.option(form.DummyValue, 'Gateway', _('Gateway'));

		o = s.taboption('detail', form.SectionValue, '_cont_', form.TableSection, 'Containers', _('Containers'));
		ss = o.subsection;
		ss.anonymous = true;

		o = ss.option(form.DummyValue, 'Name', _('Name'));
		o.cfgvalue = function(sid) {
			const val = this.data?.[sid] ?? this.map.data.get(this.map.config, sid, this.option);
			const containerId = container_list.find(c => c.Names.find(e => e.substring(1) === val)).Id;
			return E('a', {
				href: `${view.dockerman_url}/container/${containerId}`,
				title: containerId,
				style: 'white-space: nowrap;'
			}, [val]);
		};

		ss.option(form.DummyValue, 'MacAddress', _('Mac Address'));
		ss.option(form.DummyValue, 'IPv4Address', _('IPv4 Address'));

		// Show IPv6 column when at least one entry contains a non-empty IPv6Address
		const _networkContainers = Object.values(this_network?.Containers || {});
		const _hasIPv6 = _networkContainers.some(c => c?.IPv6Address && String(c.IPv6Address).trim() !== '');
		if (_hasIPv6) {
			ss.option(form.DummyValue, 'IPv6Address', _('IPv6 Address'));
		}

		// INSPECT TAB

		s.tab('inspect', _('Inspect'));

		o = s.taboption('inspect', form.SectionValue, '__ins__', form.NamedSection, '_inspect', null);
		ss = o.subsection;
		ss.anonymous = true;
		ss.nodescriptions = true;

		o = ss.option(form.Button, '_inspect_button', null);
		o.inputtitle = `${dm2.ActionTypes['inspect'].i18n} ${dm2.ActionTypes['inspect'].e}`;
		o.inputstyle = 'neutral';
		o.onclick = L.bind(function(section_id, ev) {
			return dm2.network_inspect({ id: this_network.Id }).then((response) => {
				const inspectField = document.getElementById('inspect-output-text');
				if (inspectField && response?.body) {
					inspectField.textContent = JSON.stringify(response.body, null, 2);
				}
			});
		}, this);

		o = s.taboption('inspect', form.SectionValue, '__insoutput__', form.NamedSection, null, null);
		o.render = L.bind(() => {
			return this.insertOutputFrame(null, null);
		}, this);

		return m.render();
	},

	handleSave: null,
	handleSaveApply: null,
	handleReset: null,

});

```

---

# network_new.js
```javascript
'use strict';
'require form';
'require fs';
'require ui';
'require tools.widgets as widgets';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/


return dm2.dv.extend({
	load() {
		return Promise.all([

		]);
	},

	render() {

		// stuff JSONMap with {network: {}} to prime it with a new empty entry
		const m = new form.JSONMap({network: {}}, _('Docker - New Network'));
		m.submit = true;
		m.reset = true;

		let s = m.section(form.NamedSection, 'network', _('Create new docker network'));
		s.anonymous = true;
		s.nodescriptions = true;
		s.addremove = false;

		let o;

		o = s.option(form.Value, 'name', _('Network Name'),
			_('Name of the network that can be selected during container creation'));
		o.rmempty = true;

		o = s.option(form.ListValue, 'driver', _('Driver'));
		o.rmempty = true;
		o.value('bridge', _('Bridge device'));
		o.value('macvlan', _('MAC VLAN'));
		o.value('ipvlan',  _('IP VLAN'));
		o.value('overlay', _('Overlay network'));

		o = s.option(widgets.DeviceSelect, 'parent', _('Base device'));
		o.rmempty = true;
		o.create = false
		o.noaliases = true;
		o.nocreate = true;
		o.depends('driver', 'macvlan');

		o = s.option(form.ListValue, 'macvlan_mode', _('Mode'));
		o.rmempty = true;
		o.depends('driver', 'macvlan');
		o.default = 'bridge';
		o.value('bridge', _('Bridge (Support direct communication between MAC VLANs)'));
		o.value('private', _('Private (Prevent communication between MAC VLANs)'));
		o.value('vepa', _('VEPA (Virtual Ethernet Port Aggregator)'));
		o.value('passthru', _('Pass-through (Mirror physical device to single MAC VLAN)'));

		o = s.option(form.ListValue, 'ipvlan_mode', _('Ipvlan Mode'));
		o.rmempty = true;
		o.depends('driver', 'ipvlan');
		o.default='l3';
		o.value('l2', _('L2 bridge'));
		o.value('l3', _('L3 bridge'));

		o = s.option(form.Flag, 'ingress',
			_('Ingress'),
			_('Ingress network is the network which provides the routing-mesh in swarm mode'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = 0;
		o.depends('driver', 'overlay');

		o = s.option(form.DynamicList, 'options', _('Options'));
		o.rmempty = true;
		o.placeholder='com.docker.network.driver.mtu=1500';

		o = s.option(form.DynamicList, 'labels', _('Labels'));
		o.rmempty = true;
		o.placeholder='foo=bar';

		o = s.option(form.Flag, 'internal', _('Internal'), _('Restrict external access to the network'));
		o.rmempty = true;
		o.depends('driver', 'overlay');
		o.disabled = 0;
		o.enabled = 1;
		o.default = o.disabled;

		// if nixio.fs.access('/etc/config/network') and nixio.fs.access('/etc/config/firewall')then
		// 	o = s.option(form.Flag, 'op_macvlan', _('Create macvlan interface'), _('Auto create macvlan interface in Openwrt'))
		// 	o.depends('driver', 'macvlan')
		// 	o.disabled = 0
		// 	o.enabled = 1
		// 	o.default = 1
		// end

		o = s.option(form.Value, 'subnet', _('Subnet'));
		o.rmempty = true;
		o.placeholder = '10.1.0.0/16';
		o.datatype = 'ip4addr';

		o = s.option(form.Value, 'gateway', _('Gateway'));
		o.rmempty = true;
		o.placeholder = '10.1.1.1';
		o.datatype = 'ip4addr';

		o = s.option(form.Value, 'ip_range', _('IP range'));
		o.rmempty = true;
		o.placeholder='10.1.1.0/24';
		o.datatype = 'ip4addr';

		o = s.option(form.DynamicList, 'aux_address', _('Exclude IPs'));
		o.rmempty = true;
		o.placeholder = 'my-route=10.1.1.1';

		o = s.option(form.Flag, 'ipv6', _('Enable IPv6'));
		o.rmempty = true;
		o.disabled = 0;
		o.enabled = 1;
		o.default = o.disabled;

		o = s.option(form.Value, 'subnet6', _('IPv6 Subnet'));
		o.rmempty = true;
		o.placeholder='fe80::/10'
		o.datatype = 'ip6addr';
		o.depends('ipv6', 1);

		o = s.option(form.Value, 'gateway6', _('IPv6 Gateway'));
		o.rmempty = true;
		o.placeholder='fe80::1';
		o.datatype = 'ip6addr';
		o.depends('ipv6', 1);

		this.map = m;

		return m.render();

	},

	handleSave(ev) {
		ev?.preventDefault();

		const view = this;

		const map = this.map;
		if (!map)
			return Promise.reject(new Error(_('Form is not ready yet.')));

		const listToKv = view.listToKv;

		const toBool = (val) => (val === 1 || val === '1' || val === true);

		return map.parse()
			.then(() => {
				const get = (opt) => map.data.get('json', 'network', opt);
				const name = get('name');
				const driver = get('driver');
				const internal = toBool(get('internal'));
				const ingress = toBool(get('ingress'));
				const ipv6 = toBool(get('ipv6'));
				const subnet = get('subnet');
				const gateway = get('gateway');
				const ipRange = get('ip_range');
				const auxAddress = listToKv(get('aux_address'));
				const optionsList = listToKv(get('options'));
				const labelsList = listToKv(get('labels'));
				const subnet6 = get('subnet6');
				const gateway6 = get('gateway6');

				const createBody = {
					Name: name,
					Driver: driver,
					EnableIPv6: ipv6,
					IPAM: {
						Driver: 'default'
					},
					Internal: internal,
					Labels: labelsList,
				};

				if (subnet || gateway || ipRange
					|| (auxAddress && typeof auxAddress === 'object' && Object.keys(auxAddress).length)) {
					createBody.IPAM.Config = [{
						Subnet: subnet,
						Gateway: gateway,
						IPRange: ipRange,
						AuxAddress: auxAddress,
						AuxiliaryAddresses: auxAddress,
					}];
				}

				if (driver === 'macvlan') {
					createBody.Options = {
						macvlan_mode: get('macvlan_mode'),
						parent: get('parent'),
					};
				}
				else if (driver === 'ipvlan') {
					createBody.Options = {
						ipvlan_mode: get('ipvlan_mode'),
					};
				}
				else if (driver === 'overlay') {
					createBody.Ingress = ingress;
				}

				if (ipv6 && (subnet6 || gateway6)) {
					createBody.IPAM.Config = createBody.IPAM.Config || [];
					createBody.IPAM.Config.push({
						Subnet: subnet6,
						Gateway: gateway6,
					});
				}

				if (optionsList && typeof optionsList === 'object' && Object.keys(optionsList).length) {
					createBody.Options = Object.assign(createBody.Options || {}, optionsList);
				}

				if (labelsList && typeof labelsList === 'object' && Object.keys(labelsList).length) {
					createBody.Labels = Object.assign(createBody.Labels || {}, labelsList);
				}

				return createBody;
			})
			.then((createBody) => view.executeDockerAction(
				dm2.network_create,
				{ body: createBody },
				_('Create network'),
				{
					showOutput: false,
					showSuccess: false,
					onSuccess: (response) => {
						if (response?.body?.Warning) {
							view.showNotification(_('Network created with warning'), response.body.Warning, 5000, 'warning');
						} else {
							view.showNotification(_('Network created'), _('OK'), 4000, 'success');
						}
						window.location.href = `${this.dockerman_url}/networks`;
					}
				}
			))
			.catch((err) => {
				view.showNotification(_('Create network failed'), err?.message || String(err), 7000, 'error');
				return false;
			});
	},

	handleSaveApply: null,
	handleReset: null,

});

```

---

# networks.js
```javascript
'use strict';
'require form';
'require fs';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/


return dm2.dv.extend({
	load() {
		return Promise.all([
			dm2.network_list(),
			dm2.container_list({query: {all: true}}),
		]);
	},

	render([networks, containers]) {
		if (networks?.code !== 200) {
			return E('div', {}, [ networks?.body?.message ]);
		}

		let network_list = this.getNetworksTable(networks.body, containers.body);
		// let container_list = containers.body;
		const view = this; // Capture the view context


		let pollPending = null;
		let netSec = null;

		const refresh = () => {
			if (pollPending) return pollPending;
			pollPending = view.load().then(([networks2, containers2]) => {
				network_list = view.getNetworksTable(networks2.body, containers2.body);
				// container_list = containers2.body;
				m.data = new m.data.constructor({network: network_list, prune: {}});

				if (netSec) {
					netSec.footer = [
						`${_('Total')} ${network_list.length}`,
					];
				}

				return m.render();
			}).catch((err) => { console.warn(err) }).finally(() => { pollPending = null });
			return pollPending;
		};


		let s, o;
		const m = new form.JSONMap({network: network_list, prune: {}},
			_('Docker - Networks'),
			_('This page displays all docker networks that have been created on the connected docker host.'));
		m.submit = false;
		m.reset = false;

		s = m.section(form.TableSection, 'prune', _('Networks overview'), null);
		s.addremove = false;
		s.anonymous = true;

		const prune = s.option(form.Button, '_prune', null);
		prune.inputtitle = `${dm2.ActionTypes['prune'].i18n} ${dm2.ActionTypes['prune'].e}`;
		prune.inputstyle = 'negative';
		prune.onclick = L.bind(function(section_id, ev) {

			return this.super('handleXHRTransfer', [{
				q_params: {  },
				commandCPath: '/networks/prune',
				commandDPath: '/networks/prune',
				commandTitle: dm2.ActionTypes['prune'].i18n,
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['prune'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				noFileUpload: true,
			}]);

			// return view.executeDockerAction(
			// 	dm2.network_prune,
			// 	{ query: { filters: '' } },
			// 	dm2.ActionTypes['prune'].i18n,
			// 	{
			// 		showOutput: true,
			// 		successMessage: _('started/completed'),
			// 		onSuccess: () => {
			// 			setTimeout(() => window.location.href = `${this.dockerman_url}/networks`, 1000);
			// 		}
			// 	}
			// );
		}, this);

		netSec = m.section(form.TableSection, 'network');
		netSec.anonymous = true;
		netSec.nodescriptions = true;
		netSec.addremove = true;
		netSec.sortable = true;
		netSec.filterrow = true;
		netSec.addbtntitle = `${dm2.ActionTypes['create'].i18n} ${dm2.ActionTypes['create'].e}`;
		netSec.footer = [
			`${_('Total')} ${network_list.length}`,
		];

		netSec.handleAdd = function(section_id, ev) {
			window.location.href = `${view.dockerman_url}/network_new`;
		};

		netSec.handleRemove = function(section_id, force, ev) {
			const network = network_list.find(net => net['.name'] === section_id);
			if (!network?.Id) return false;

			return view.executeDockerAction(
				dm2.network_remove,
				{ id: network.Id },
				dm2.ActionTypes['remove'].i18n,
				{
					showOutput: true,
					onSuccess: () => {
						return refresh();
					}
				}
			);
		};

		netSec.handleInspect = function(section_id, ev) {
			const network = network_list.find(net => net['.name'] === section_id);
			if (!network?.Id) return false;

			return view.executeDockerAction(
				dm2.network_inspect,
				{ id: network.Id },
				dm2.ActionTypes['inspect'].i18n,
				{ showOutput: true, showSuccess: false }
			);
		};

		netSec.renderRowActions = function (section_id) {
			const network = network_list.find(net => net['.name'] === section_id);
			const btns = [
				E('button', {
					'class': 'cbi-button view',
					'title': dm2.ActionTypes['inspect'].i18n,
					'click': ui.createHandlerFn(this, this.handleInspect, section_id),
				}, [dm2.ActionTypes['inspect'].e]),

				E('div', {
					'style': 'width: 20px',
					// Some safety margin for mis-clicks
				}, [' ']),

				E('button', {
					'class': 'cbi-button cbi-button-negative remove',
					'title': dm2.ActionTypes['remove'].i18n,
					'click': ui.createHandlerFn(this, this.handleRemove, section_id, false),
					'disabled': network?._disable_delete,
				}, dm2.ActionTypes['remove'].e),
				E('button', {
					'class': 'cbi-button cbi-button-negative important remove',
					'title': dm2.ActionTypes['force_remove'].i18n,
					'click': ui.createHandlerFn(this, this.handleRemove, section_id, true),
					'disabled': network?._disable_delete,
				}, dm2.ActionTypes['force_remove'].e),
			];
			return E('td', { 'class': 'td middle cbi-section-actions' }, E('div', btns));
		};

		o = netSec.option(form.DummyValue, '_shortId', _('ID'));

		o = netSec.option(form.DummyValue, 'Name', _('Name'));

		o = netSec.option(form.DummyValue, 'Labels', _('Labels') + '  🏷️');
		o.cfgvalue = view.objectCfgValueTT;

		o = netSec.option(form.DummyValue, '_container', _('Containers'));

		o = netSec.option(form.DummyValue, 'Driver', _('Driver'));

		o = netSec.option(form.DummyValue, '_interface', _('Parent Interface'));

		o = netSec.option(form.DummyValue, '_subnet', _('Subnet'));

		o = netSec.option(form.DummyValue, '_gateway', _('Gateway'));

		this.insertOutputFrame(s, m);

		return m.render();
	},

	handleSave: null,
	handleSaveApply: null,
	handleReset: null,

	getNetworksTable(networks, containers) {
		const data = [];

		for (const [ , net] of (networks || []).entries()) {
			const n = net.Name;
			const _shortId = (net.Id || '').substring(0, 12);
			const shortLink = E('a', {
				'href': `${view.dockerman_url}/network/${net.Id}`,
				'style': 'font-family: monospace;',
				'title': _('Click to view this network'),
			}, [_shortId]);

			// Just push plain data objects without UCI metadata
			const configs = Array.isArray(net?.IPAM?.Config) ? net.IPAM.Config : [];
			data.push({
				...net,
				_gateway: configs.map(o => o.Gateway).filter(o => o).join(', ') || '',
				_subnet: configs.map(o => o.Subnet).filter(o => o).join(', ') || '',
				_disable_delete: ( n === 'bridge' || n === 'none' || n === 'host' ) ? true : null,
				_shortId: shortLink,
				_container: this.parseContainerLinksForNetwork(net, containers),
				_interface: (net.Driver === 'bridge')
					? net.Options?.['com.docker.network.bridge.name'] || ''
					: (net.Driver === 'macvlan')
						? net?.Options?.parent
						: '',
			});
		}

		return data;
	},

});

```

---

# overview.js
```javascript
'use strict';
'require form';
'require fs';
'require uci';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/

/**
 * Returns a Set of image IDs in use by containers
 * @param {Array} containers - Array of container objects
 * @returns {Set<string>} Set of image IDs
 */
function getImagesInUseByContainers(containers) {
	const inUse = new Set();
	for (const c of containers || []) {
		if (c.ImageID) inUse.add(c.ImageID);
		else if (c.Image) inUse.add(c.Image);
	}
	return inUse;
}

/**
 * Returns a Set of network IDs in use by containers
 * @param {Array} containers - Array of container objects
 * @returns {Set<string>} Set of network IDs
 */
function getNetworksInUseByContainers(containers) {
	const inUse = new Set();
	for (const c of containers || []) {
		const networks = c.NetworkSettings?.Networks;
		if (networks && typeof networks === 'object') {
			for (const netName in networks) {
				const net = networks[netName];
				if (net.NetworkID) inUse.add(net.NetworkID);
				else if (netName) inUse.add(netName);
			}
		}
	}
	return inUse;
}

/**
 * Returns a Set of volume mountpoints in use by containers
 * @param {Array} containers - Array of container objects
 * @returns {Set<string>} Set of volume names or mountpoints
 */
function getVolumesInUseByContainers(containers) {
	const inUse = new Set();
	for (const c of containers || []) {
		const mounts = c.Mounts;
		if (Array.isArray(mounts)) {
			for (const m of mounts) {
				if (m.Type === 'volume' && m.Name) inUse.add(m.Name);
			}
		}
	}
	return inUse;
}


return dm2.dv.extend({
	load() {
		// const now = Math.floor(Date.now() / 1000);

		return Promise.all([
			dm2.docker_version(),
			dm2.docker_info(),
			// dm2.docker_df(), // takes > 20 seconds on large docker environments
			dm2.container_list().then(r => r.body || []),
			dm2.image_list().then(r => r.body || []),
			dm2.network_list().then(r => r.body || []),
			dm2.volume_list().then(r => r.body || []),
			dm2.callMountPoints(),
		]);
	},

	handleAction(name, action, ev) {
		return dm2.callRcInit(name, action).then(function(ret) {
			if (ret)
				throw _('Command failed');

			return true;
		}).catch(function(e) {
			L.ui.addTimeLimitedNotification(null, E('p', _('Failed to execute "/etc/init.d/%s %s" action: %s').format(name, action, e)), 5000, 'warning');
		});
	},

	render([version_response,
			info_response,
			// df_response,
			container_list,
			image_list,
			network_list,
			volume_list,
			mounts,
		]) {
		const version_headers = [];
		const version_body = [];
		const info_body = [];
		// const df_body = [];
		const docker_ep = uci.get('dockerd', 'globals', 'hosts');
		let isLocal = false;
		if (!docker_ep || docker_ep.length === 0 || docker_ep.map(e => e.includes('.sock')).filter(Boolean).length == 1)
			isLocal = true;

		if (info_response?.code !== 200) {
			return E('div', {}, [ info_response?.body?.message ]);
		}

		this.parseHeaders(version_response.headers, version_headers);
		this.parseBody(version_response.body, version_body);
		this.parseBody(info_response.body, info_body);
		// this.parseBody(df_response.body, df_body);
		const view = this;
		const info = info_response.body;

		this.concount = info?.Containers || 0;
		this.conactivecount = info?.ContainersRunning || 0;

		/* Because the df function that reconciles Volumes, Networks and Containers
		is slow on large and busy dockerd endpoints, we do it here manually. It's fast. */
		this.imgcount = image_list.length;
		this.imgactivecount = getImagesInUseByContainers(container_list)?.size || 0;

		this.netcount = network_list.length;
		this.netactivecount = getNetworksInUseByContainers(container_list)?.size || 0;

		this.volcount = volume_list?.Volumes?.length;
		this.volactivecount = getVolumesInUseByContainers(container_list)?.size || 0;

		this.freespace = isLocal ? mounts.find(m => m.mount === info?.DockerRootDir)?.avail || 0 : 0;
		if (isLocal && this.freespace !== 0)
			this.freespace = '(' + '%1024.2m'.format(this.freespace) + ' ' + _('Available') + ')';

		const mainContainer = E('div', { 'class': 'cbi-map' });

		// Add heading and description first
		mainContainer.appendChild(E('h2', { 'class': 'section-title' }, [_('Docker - Overview')]));
		mainContainer.appendChild(E('div', { 'class': 'cbi-map-descr' }, [
			_('An overview with the relevant data is displayed here with which the LuCI docker client is connected.'),
			E('br'),
			E('a', { href: 'https://github.com/openwrt/luci/blob/master/applications/luci-app-dockerman/README.md' }, ['README'])
		]));

		if (isLocal)
			mainContainer.appendChild(E('div', { 'class': 'cbi-section' }, [
				E('div', { 'style': 'display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 10px;' }, [
					E('button', { 'class': 'btn cbi-button-action neutral', 'click': () => this.handleAction('dockerd', 'restart') }, _('Restart', 'daemon restart action')),
					E('button', { 'class': 'btn cbi-button-action negative', 'click': () => this.handleAction('dockerd', 'stop') }, _('Stop', 'daemon stop action')),
				])
			]));

		// Create the info table
		const summaryTable = new L.ui.Table(
			[_('Info'), ''],
			{ id: 'containers-table', style: 'width: 100%; table-layout: auto;' },
			[]
		);

		summaryTable.update([
			[ _('Docker Version'), version_response.body.Version ],
			[ _('Api Version'), version_response.body.ApiVersion ],
			[ _('CPUs'), info_response.body.NCPU ],
			[ _('Total Memory'), '%1024.2m'.format(info_response.body.MemTotal) ],
			[ _('Docker Root Dir'), `${info_response.body.DockerRootDir} ${ (isLocal && this.freespace) ? this.freespace : '' }` ],
			[ _('Index Server Address'), info_response.body.IndexServerAddress ],
			[ _('Registry Mirrors'), info_response.body.RegistryConfig?.Mirrors || '-' ],
		]);

		// Wrap the table in a cbi-section
		mainContainer.appendChild(E('div', { 'class': 'cbi-section' }, [
			summaryTable.render()
		]));


		// Create a container div with grid layout for the status badges
		let statusContainer = E('div', { style: 'display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-bottom: 20px;' }, [
			this.overviewBadge(`${this.dockerman_url}/containers`,
				E('img', {
					src: L.resource('dockerman/containers.svg'),
					style: 'width: 80px; height: 80px;'
				}, []),
				_('Containers'),
				_('Total: '),
				view.concount,
				_('Running: '),
				view.conactivecount),
			this.overviewBadge(`${this.dockerman_url}/images`,
				E('img', {
					src: L.resource('dockerman/images.svg'),
					style: 'width: 80px; height: 80px;'
				}, []),
				_('Images'),
				_('Total: '),
				view.imgcount,
				view.imgactivecount ? _('In Use: ') : '',
				view.imgactivecount ? view.imgactivecount : ''),
			this.overviewBadge(`${this.dockerman_url}/networks`,
				E('img', {
					src: L.resource('dockerman/networks.svg'),
					style: 'width: 80px; height: 80px;'
				}, []),
				_('Networks'),
				_('Total: '),
				view.netcount,
				view.netactivecount ? _('In Use: ') : '',
				view.netactivecount ? view.netactivecount : ''),
			this.overviewBadge(`${this.dockerman_url}/volumes`,
				E('img', {
					src: L.resource('dockerman/volumes.svg'),
					style: 'width: 80px; height: 80px;'
				}, []),
				_('Volumes'),
				_('Total: '),
				view.volcount,
				view.volactivecount ? _('In Use: ') : '',
				view.volactivecount ? view.volactivecount : ''),
		]);

		// Add badges section
		mainContainer.appendChild(statusContainer);

		const m = new form.JSONMap({
			// df: df_body,
			vb: version_body,
			ib: info_body
		});
		m.readonly = true;
		m.tabbed = false;

		let s;

		// Add Version and Environment tables
		s = m.section(form.TableSection, 'vb', _('Version'));
		s.anonymous = true;

		s.option(form.DummyValue, 'entry', _('Name'));
		s.option(form.DummyValue, 'value', _('Value'));

		s = m.section(form.TableSection, 'ib', _('Environment'));
		s.anonymous = true;
		s.filterrow = true;

		s.option(form.DummyValue, 'entry', _('Entry'));
		s.option(form.DummyValue, 'value', _('Value'));

		// Render the form sections and append them
		return m.render()
			.then(fe => {
				mainContainer.appendChild(fe);
				return mainContainer;
			});
	},

	overviewBadge(url, resource_div, caption, total_caption, total_count, active_caption, active_count) {
		return E('a', { href: url, style: 'text-decoration: none; cursor: pointer;', title: _('Go to relevant configuration page') }, [
				E('div', { style: 'border: 1px solid #ddd; border-radius: 5px; padding: 15px; min-height: 120px; display: flex; align-items: center;' }, [
					E('div', { style: 'flex: 0 0 auto; margin-right: 15px;' }, [
						resource_div,
					]),
					E('div', { style: 'flex: 1;' }, [
						E('div', { style: 'font-size: 20px; font-weight: bold; color: #333; margin-bottom: 8px;' }, caption),
						E('div', { style: 'font-size: 16px; margin: 4px 0;' }, [
							E('span', { style: 'color: #666; margin-right: 10px;' }, [total_caption, E('strong', { style: 'color: #0066cc;' }, total_count)])
						]),
						E('div', { style: 'font-size: 16px; margin: 4px 0;' }, [
							E('span', { style: 'color: #666;' }, [active_caption, E('strong', { style: 'color: #28a745;' }, active_count)])
						])
					])
				])
			])

	}
});

```

---

# volumes.js
```javascript
'use strict';
'require form';
'require fs';
'require ui';
'require dockerman.common as dm2';

/*
Copyright 2026
Docker manager JS for Luci by Paul Donald <newtwen+github@gmail.com> 
Based on Docker Lua by lisaac <https://github.com/lisaac/luci-app-dockerman>
LICENSE: GPLv2.0
*/


return dm2.dv.extend({
	load() {
		return Promise.all([
			dm2.volume_list(),
			dm2.container_list({query: {all: true}}),
		]);
	},

	render([volumes, containers]) {
		if (volumes?.code !== 200) {
			return E('div', {}, [ volumes.body.message ]);
		}

		// this.volumes = volumes || {};
		let container_list = containers.body || [];
		let volume_list = this.getVolumesTable(volumes.body);
		const view = this; // Capture the view context

		let pollPending = null;
		let volSec = null;

		const refresh = () => {
			if (pollPending) return pollPending;
			pollPending = view.load().then(([volumes2, containers2]) => {
				volume_list = view.getVolumesTable(volumes2.body);
				container_list = containers2.body;
				m.data = new m.data.constructor({volume: volume_list, prune: {}});

				if (volSec) {
					volSec.footer = [
						`${_('Total')} ${volume_list.length}`,
					];
				}

				return m.render();
			}).catch((err) => { console.warn(err) }).finally(() => { pollPending = null });
			return pollPending;
		};

		let s, o;
		const m = new form.JSONMap({volume: volume_list, prune: {}},
			_('Docker - Volumes'),
			_('This page displays all docker volumes that have been created on the connected docker host.'));
		m.submit = false;
		m.reset = false;

		s = m.section(form.TableSection, 'prune', null, _('Volumes overview'));
		s.addremove = false;
		s.anonymous = true;
		const prune = s.option(form.Button, '_prune', null);
		prune.inputtitle = `${dm2.ActionTypes['prune'].i18n} ${dm2.ActionTypes['prune'].e}`;
		prune.inputstyle = 'negative';
		prune.onclick = L.bind(function(sid, ev) {

			return this.super('handleXHRTransfer', [{
				q_params: {  },
				commandCPath: '/volumes/prune',
				commandDPath: '/volumes/prune',
				commandTitle: dm2.ActionTypes['prune'].i18n,
				onUpdate: (msg) => {
					try {
						if(msg.error)
							ui.addTimeLimitedNotification(dm2.ActionTypes['prune'].i18n, msg.error, 7000, 'error');

						const output = JSON.stringify(msg, null, 2) + '\n';
						view.insertOutput(output);
					} catch {

					}
				},
				noFileUpload: true,
			}]);

			// return view.executeDockerAction(
			// 	dm2.volume_prune,
			// 	{ query: { filters: '' } },
			// 	dm2.ActionTypes['prune'].i18n,
			// 	{
			// 		showOutput: true,
			// 		successMessage: _('started/completed'),
			// 		onSuccess: () => {
			// 			setTimeout(() => window.location.href = `${this.dockerman_url}/volumes`, 1000);
			// 		}
			// 	}
			// );
		}, this);


		volSec = m.section(form.TableSection, 'volume');
		volSec.anonymous = true;
		volSec.nodescriptions = true;
		volSec.addremove = true;
		volSec.sortable = true;
		volSec.filterrow = true;
		volSec.addbtntitle = `${dm2.ActionTypes['create'].i18n} ${dm2.ActionTypes['create'].e}`;
		volSec.footer = [
			`${_('Total')} ${volume_list.length}`,
		];

		volSec.handleAdd = function(ev) {

			ev.preventDefault();
			let nameInput, labelsInput;
			return ui.showModal(_('New volume'), [
				E('p', {}, _('Enter an optional name and labels for the new volume')),
				E('div', { 'class': 'cbi-value' }, [
					E('label', { 'class': 'cbi-value-title' }, _('Name')),
					E('div', { 'class': 'cbi-value-field' }, [
						nameInput = E('input', {
							'type': 'text',
							'class': 'cbi-input-text',
							'placeholder': _('volume name'),
						})
					])
				]),

				E('div', { 'class': 'cbi-value' }, [
					E('label', { 'class': 'cbi-value-title' }, _('Labels')),
					E('div', { 'class': 'cbi-value-field' }, [
						labelsInput = E('input', {
							'type': 'text',
							'class': 'cbi-input-text',
							'placeholder': 'key=value, key2=value2, ...',
						})
						// labelsInput = new ui.DynamicList([], [], {}).render(),
					])
				]),


				E('div', { 'class': 'right' }, [
					E('button', {
						'class': 'cbi-button',
						'click': ui.hideModal
					}, ['↩']),
					' ',
					E('button', {
						'class': 'cbi-button cbi-button-positive',
						'click': ui.createHandlerFn(view, () => {
							const name = nameInput.value.trim();
							const labels = Object.fromEntries(
								(labelsInput.value.trim()?.split(',') || [])
									.map(e => e.trim())
									.filter(Boolean)
									.map(e => e.split('='))
									.filter(pair => pair.length === 2)
							);

							ui.hideModal();

							return view.executeDockerAction(
								dm2.volume_create,
								{ opts: { Name: name, Labels: labels } },
								dm2.Types['volume'].sub['create'].i18n,
								{
									showOutput: true,
									onSuccess: () => {
										return refresh();
									}
								}
							);
						})
					}, [dm2.Types['volume'].sub['create'].e])
				])
			]);
		};

		volSec.handleRemove = function(sid, force, ev) {
			const volume = volume_list.find(net => net['.name'] === sid);

			if (!volume?.Name) return false;

			return view.executeDockerAction(
				dm2.volume_remove,
				{ id: volume.Name, query: { force: force } },
				dm2.ActionTypes['remove'].i18n,
				{
					showOutput: true,
					onSuccess: () => {
						return refresh();
					}
				}
			);
		};

		volSec.handleInspect = function(sid, ev) {
			const volume = volume_list.find(net => net['.name'] === sid);

			if (!volume?.Name) return false;

			return view.executeDockerAction(
				dm2.volume_inspect,
				{ id: volume.Name },
				dm2.ActionTypes['inspect'].i18n,
				{ showOutput: true, showSuccess: false }
			);
		};

		volSec.renderRowActions = function (sid) {
			const volume = volume_list.find(net => net['.name'] === sid);
			const btns = [
				E('button', {
					'class': 'cbi-button view',
					'title': dm2.ActionTypes['inspect'].i18n,
					'click': ui.createHandlerFn(this, this.handleInspect, sid),
				}, [dm2.ActionTypes['inspect'].e]),

				E('div', {
					'style': 'width: 20px',
					// Some safety margin for mis-clicks
				}, [' ']),

				E('button', {
					'class': 'cbi-button cbi-button-negative remove',
					'title': dm2.ActionTypes['remove'].i18n,
					'click': ui.createHandlerFn(this, this.handleRemove, sid, false),
					'disabled': volume?._disable_delete,
				}, [dm2.ActionTypes['remove'].e]),
				E('button', {
					'class': 'cbi-button cbi-button-negative important remove',
					'title': dm2.ActionTypes['force_remove'].i18n,
					'click': ui.createHandlerFn(this, this.handleRemove, sid, true),
				}, [dm2.ActionTypes['force_remove'].e]),
			];
			return E('td', { 'class': 'td middle cbi-section-actions' }, E('div', btns));
		};

		volSec.option(form.DummyValue, '_name', _('Name'));

		o = volSec.option(form.DummyValue, 'Labels', _('Labels') + '  🏷️');
		o.cfgvalue = view.objectCfgValueTT;

		volSec.option(form.DummyValue, 'Driver', _('Driver'));

		o = volSec.option(form.DummyValue, 'Containers', _('Containers'));
		o.cfgvalue = function(sid) {
			const vol = this.map.data.data[sid] || {};
			return view.parseContainerLinksForVolume(vol, container_list);
		};

		o = volSec.option(form.DummyValue, 'Mountpoint', _('Mount Point'));
		o.cfgvalue = function(sid) {
			const mp = this.map.data.get(this.map.config, sid, this.option);
			if (!mp) return;
			// Try to match Docker volume mountpoint pattern: /var/lib/docker/volumes/<id>/_data
			const match = mp.match(/^(.*\/volumes\/)([^/]+)(\/.*)?$/);
			if (match && match[2].length > 36) {
				// Show the first 12 characters of the ID portion
				return match[1] + match[2].substring(0, 12) + '...' + (match[3] || '');
			}
			return mp;
		};

		o = volSec.option(form.DummyValue, 'CreatedAt', _('Created'));

		this.insertOutputFrame(s, m);

		return m.render();
	},

	handleSave: null,
	handleSaveApply: null,
	handleReset: null,

	getVolumesTable(volumes) {
		const data = [];

		for (const [ , vol] of (volumes?.Volumes || []).entries()) {
			const labels = vol?.Labels || {};

			// Just push plain data objects without UCI metadata
			data.push({
				...vol,
				Labels: labels,
				_name: (vol.Name || '').substring(0, 12),
				Containers: vol.Containers || '',
			});
		}

		return data;
	},

	parseContainerLinksForVolume(volume, containers) {
		const links = [];
		for (const cont of containers || []) {
			const mounts = cont?.Mounts || [];
			const usesVolume = mounts.some(m => {
				if (m?.Type !== 'volume' && m?.Type !== 'bind') return false;
				const byName = !!volume?.Name && m?.Name === volume.Name;
				const bySource = !!volume?.Mountpoint && (m?.Source === volume.Mountpoint || (m?.Source || '').startsWith(volume.Mountpoint));
				return byName || bySource;
			});

			if (usesVolume) {
				const containerName = cont?.Names?.[0]?.replace(/^\//, '') || (cont?.Id || '').substring(0, 12);
				const containerId = cont?.Id;
				links.push(E('a', {
					href: `${this.dockerman_url}/container/${containerId}`,
					title: containerId,
					style: 'white-space: nowrap;'
				}, [containerName]));
			}
		}

		if (!links.length)
			return '-';

		const out = [];
		for (let i = 0; i < links.length; i++) {
			out.push(links[i]);
			if (i < links.length - 1)
				out.push(' | ');
		}

		return E('div', {}, out);
	},

});

```

---

# docker_rpc.uc
```ucode
#!/usr/bin/env ucode

// Copyright 2025 Paul Donald / luci-lib-docker-js
// Licensed to the public under the Apache License 2.0.
// Built against the docker v1.47 API


'use strict';

import * as http from 'luci.http';
import * as fs from 'fs';
import * as socket from 'socket';
import { cursor } from 'uci';
import * as ds from 'luci.docker_socket';

// const cmdline = fs.readfile('/proc/self/cmdline');
// const args = split(cmdline, '\0');
const caller = trim(fs.readfile('/proc/self/comm'));

const BLOCKSIZE = 8192;
const POLL_TIMEOUT = 8000; // default; can be overridden per request
// const API_VER = '/v1.47';
const PROTOCOL = 'HTTP/1.1';
const CLIENT_VER = '1';

function merge(a, b) {
	let c = {};
	for (let k, v in a)
		c[k] = v;
	for (let k, v in b)
		c[k] = v;
	return c;
};

function chunked_body_reader(sock, initial_buffer) {
	let state = 0, chunklen = 0, buffer = initial_buffer || '';

	function poll_and_recv() {
		let ready = socket.poll(POLL_TIMEOUT, [sock, socket.POLLIN]);
		if (!ready || !length(ready)) return null;
		let data = sock.recv(BLOCKSIZE);
		if (!data) return null;
		buffer += data;
		return true;
	}

	return () => {
		while (true) {
			if (state === 0) {
				let m = match(buffer, /^([0-9a-fA-F]+)\r\n/);
				if (!m || length(m) < 2) {
					if (!poll_and_recv()) return null;
					continue;
				}
				chunklen = int(m[1], 16);
				buffer = substr(buffer, length(m[0]));
				if (chunklen === 0) return null;
				state = 1;
			}
			if (state === 1 && length(buffer) >= chunklen + 2) {
				let chunk = substr(buffer, 0, chunklen);
				buffer = substr(buffer, chunklen + 2);
				state = 0;
				return chunk;
			} else {
				if (!poll_and_recv()) return null;
				continue;
			}
		}
	};
};

function read_http_headers(response_headers, response) {
	const lines = split(response, /\r?\n/);

	for (let l in lines) {
		let kv = match(l, /([^:]+):\s*(.*)/);
		if (kv && length(kv) === 3)
			response_headers[lc(kv[1])] = kv[2];
	}

	return response_headers;
};

function get_api_ver() {

	const ctx = cursor();
	const version = ctx.get('dockerd', 'globals', 'api_version') || '';
	const version_str = version ? `/${version}` : '';
	ctx.unload();

	return version_str;
};

function coerce_values_to_string(obj) {
	for (let k, v in obj) {
		v = `${v}`;
		obj[k]=v;
	}
	return obj;
};

function call_docker(method, path, options) {
	options = options || {};
	const headers = options.headers || {};
	let payload = options.payload || null;

	/* requires ucode 2026-01-16 if get_socket_dest() provides ip:port e.g.
	'127.0.0.1:2375'.
	We use get_socket_dest_compat() which builds the SockAddress manually to
	avoid this.

	Important: dockerd after v28 won't accept tcp://x.x.x.x:2375 without
	--tls* options.

	A solution is a reverse proxy or ssh port forwarding to a remote host that
	uses the unix socket, and you still connect to a 'local port', or socket:
	ssh -L /tmp/docker.sock:localhost:2375 user@remote-host (openssh-client)
	or (dropbear)
	socat TCP-LISTEN:12375,reuseaddr,fork UNIX-CONNECT:/var/run/docker.sock
	ssh -L 2375:localhost:12375 user@remote-host
	*/


	/* works on ucode 2025-12-01 */
	const sock_dest = ds.get_socket_dest_compat();
	const sock = socket.create(sock_dest.family, socket.SOCK_STREAM);

	/* works on ucode 2026-01-16 */
	// const sock_dest = ds.get_socket_dest();
	// const sock_addr = socket.sockaddr(sock_dest);
	// const sock = socket.create(sock_addr.family, socket.SOCK_STREAM);

	if (caller != 'rpcd') {
		print('sock_dest:', sock_dest, '\n');
		// print('sock_addr:', sock_addr, '\n');
	}
	if (!sock) {
		return {
			code: 500,
			headers: {},
			body: { message: "Failed to create socket" }
		};
	}

	let conn_result = sock.connect(sock_dest);
	let err_msg = `Failed to connect to docker host at ${sock_dest}`;
	if (!conn_result) {
		sock.close();
		return {
			code: 500,
			headers: {},
			body: { message: err_msg}
		};
	}

	if (caller != 'rpcd')
		print("query: ", options.query, '\n');

	const query = options.query ? http.build_querystring(coerce_values_to_string(options.query)) : '';
	const url = path + query;

	const req_headers = [
		`${method} ${get_api_ver()}${url} ${PROTOCOL}`,
		`Host: luci-host`,
		`User-Agent: luci-app-dockerman-rpc-ucode/${CLIENT_VER}`,
		`Connection: close`
	];

	if (payload) {
		if (type(payload) === 'object') {
			payload = sprintf('%J', payload);
			headers['Content-Type'] = 'application/json';
		}
		headers['Content-Length'] = '' + length(payload);
	}

	for (let k, v in headers)
		push(req_headers, `${k}: ${v}`);

	push(req_headers, '', '');

	if (caller != 'rpcd')
		print(join('\r\n', req_headers), "\n");

	sock.send(join('\r\n', req_headers));
	if (payload) sock.send(payload);

	const response_buff = sock.recv(BLOCKSIZE);
	if (!response_buff || response_buff === '') {
		sock.close();
		return {
			code: 500,
			headers: {},
			body: { message: "No response from Docker socket" }
		};
	}
	
	const response_parts = split(response_buff, /\r?\n\r?\n/, 2);
	const response_headers = read_http_headers({}, response_parts[0]);
	let response_body;

	let is_chunked = (response_headers['transfer-encoding'] === 'chunked');

	let reader;
	if (is_chunked) {
		reader = chunked_body_reader(sock, response_parts[1]);
	}
	else if (response_headers['content-length']) {
		let content_length = int(response_headers['content-length']);
		let buf = response_parts[1];

		reader = () => {
			if (content_length <= 0) return null;

			if (buf && length(buf)) {
				let chunk = substr(buf, 0, content_length);
				buf = substr(buf, length(chunk));
				content_length -= length(chunk);
				return chunk;
			}

			let data = sock.recv(min(BLOCKSIZE, content_length));
			if (!data || data === '') return null;

			content_length -= length(data);
			return data;
		};
	}
	else {
		// Fallback for HTTP/1.0 or no content-length: read until close or timeout
		reader = () => {
			// Poll with 2 second timeout
			let ready = socket.poll(POLL_TIMEOUT, [sock, socket.POLLIN]);
			if (!ready || !length(ready)) return null; // Timeout or error

			let data = sock.recv(BLOCKSIZE);
			if (!data || data === '') return null;
			return data;
		};
	}

	let chunks = [], chunk;
	while ((chunk = reader())) {
		push(chunks, chunk);
	}

	sock.close();

	response_body = join('', chunks);

	// Parse HTTP status code
	let status_line = split(response_parts[0], /\r?\n/)[0];
	let status_match = match(status_line, /HTTP\/\S+\s+(\d+)/);
	let code = status_match ? int(status_match[1]) : 0;

	// Docker events endpoint returns newline-delimited JSON, not a single JSON object
	if (response_headers['content-type'] === 'application/json' && response_body) {
		// Single JSON object
		let data;
		try { data = json(rtrim(response_body)); }
		catch { data = null; }

		// Check if this is newline-delimited JSON (multiple lines with JSON objects)
		if (!data) {
			// Parse each line as a separate JSON object
			let lines = split(trim(response_body), /\n/);
			let events = [];
			for (let line in lines) {
				line = trim(line);
				if (line) {
					try { push(events, json(line)); }
					catch { /* skip invalid lines */ }
				}
			}
			response_body = events;
		} else {
			response_body = data;
		}
	}

	return {
		code: code,
		headers: response_headers,
		body: response_body
	};
};

function run_ttyd(request) {

	const id = request.args.id || '';
	const cmd = request.args.cmd || '/bin/sh';
	const port = request.args.port || 7682;
	const uid = request.args.uid || '';

	if (!id) {
		return { error: 'Container ID is required' };
	}

	let ttyd_cmd = `ttyd -q -d 2 --once --writable -p ${port} docker`;
	const sock_addr = ds.get_socket_dest();

	/* Build the full command:
	ttyd --writable -d 2 --once -p PORT docker -H unix://SOCKET exec -it [-u UID] CONTAINER CMD

	if the socket is /var/run/docker.sock, prefix unix://

	Note: invocations of docker -H x.x.x.x:2375 [..] will fail after v27 without --tls*
	*/
	const sock_str = index(sock_addr, '/') != -1 && index(sock_addr, 'unix://') == -1 ? 'unix://' + sock_addr : sock_addr;
	ttyd_cmd = `${ttyd_cmd} -H "${sock_str}" exec -it`;
	if (uid && uid !== '') {
		ttyd_cmd = `${ttyd_cmd} -u ${uid}`;
	}

	ttyd_cmd = `${ttyd_cmd} ${id} ${cmd} &`;

	// Try to kill any existing ttyd processes on this port
	system(`pkill -f "ttyd.*-p ${port}"` + ' 2>/dev/null; true');

	// Start ttyd
	system(ttyd_cmd);

	return { status: 'ttyd started', command: ttyd_cmd };
}

// https://docs.docker.com/reference/api/engine/version/v1.47/

/* Note: methods here are included for structural reference. Some rpcd methods
are not suitable to be called from the GUI because they are streaming endpoints
or the operations in a busy dockerd cluster take a *long* time which causes
timeouts at the front end. Good examples of this are:
- /system/df 
- push
- pull
- all /prune

We include them here because they can be useful from the command line.
*/

const core_methods = {
	version: { call: () => call_docker('GET', '/version') },
	info:    { call: () => call_docker('GET', '/info') },
	ping:    { call: () => call_docker('GET', '/_ping') },
	df:      { call: () => call_docker('GET', '/system/df') },
	events:  { args: { query: { 'since': '', 'until': `${time()}`, 'filters': '' } }, call: (request) => call_docker('GET', '/events', { query: request?.args?.query }) },
};

const exec_methods = {
	start:   { args: { id: '', body: '' }, call: (request) => call_docker('POST', `/exec/${request.args.id}/start`, { payload: request.args.body }) },
	resize:  { args: { id: '', query: { 'h': 0, 'w': 0 } }, call: (request) => call_docker('POST', `/exec/${request.args.id}/resize`, { query: request.args.query }) },
	inspect: { args: { id: '' }, call: (request) => call_docker('GET', `/exec/${request.args.id}/json`) },
};

const container_methods = {
	list:    { args: { query: { 'all': false, 'limit': false, 'size': false, 'filters': '' } }, call: (request) => call_docker('GET', '/containers/json', { query: request.args.query }) },
	create:  { args: { query: { 'name': '', 'platform': '' }, body: {} }, call: (request) => call_docker('POST', '/containers/create', { query: request.args.query, payload: request.args.body }) },
	inspect: { args: { id: '', query: { 'size': false } }, call: (request) => call_docker('GET', `/containers/${request.args.id}/json`, { query: request.args.query }) },
	top:     { args: { id: '', query: { 'ps_args': '' } }, call: (request) => call_docker('GET', `/containers/${request.args.id}/top`, { query: request.args.query }) },
	logs:    { args: { id: '', query: {} }, call: (request) => call_docker('GET', `/containers/${request.args.id}/logs`, { query: request.args.query }) },
	changes: { args: { id: '' }, call: (request) => call_docker('GET', `/containers/${request.args.id}/changes`) },
	export:  { args: { id: '' }, call: (request) => call_docker('GET', `/containers/${request.args.id}/export`) },
	stats:   { args: { id: '', query: { 'stream': false, 'one-shot': false } }, call: (request) => call_docker('GET', `/containers/${request.args.id}/stats`, { query: request.args.query }) },
	resize:  { args: { id: '', query: { 'h': 0, 'w': 0 } }, call: (request) => call_docker('POST', `/containers/${request.args.id}/resize`, { query: request.args.query }) },
	start:   { args: { id: '', query: { 'detachKeys': '' } }, call: (request) => call_docker('POST', `/containers/${request.args.id}/start`, { query: request.args.query }) },
	stop:    { args: { id: '', query: { 'signal': '', 't': 0 } }, call: (request) => call_docker('POST', `/containers/${request.args.id}/stop`, { query: request.args.query }) },
	restart: { args: { id: '', query: { 'signal': '', 't': 0 } }, call: (request) => call_docker('POST', `/containers/${request.args.id}/restart`, { query: request.args.query }) },
	kill:    { args: { id: '', query: { 'signal': '' } }, call: (request) => call_docker('POST', `/containers/${request.args.id}/kill`, { query: request.args.query }) },
	update:  { args: { id: '', body: {} }, call: (request) => call_docker('POST', `/containers/${request.args.id}/update`, { payload: request.args.body }) },
	rename:  { args: { id: '', query: { 'name': '' } }, call: (request) => call_docker('POST', `/containers/${request.args.id}/rename`, { query: request.args.query }) },
	pause:   { args: { id: '' }, call: (request) => call_docker('POST', `/containers/${request.args.id}/pause`) },
	unpause: { args: { id: '' }, call: (request) => call_docker('POST', `/containers/${request.args.id}/unpause`) },
	// attach
	// attach websocket
	// wait
	remove:  { args: { id: '', query: { 'v': false, 'force': false, 'link': false } }, call: (request) => call_docker('DELETE', `/containers/${request.args.id}`, { query: request.args.query }) },
	// archive info
	info_archive: { args: { id: '', query: { 'path': '' } }, call: (request) => call_docker('HEAD', `/containers/${request.args.id}/archive`, { query: request.args.query }) },
	// archive get
	get_archive:  { args: { id: '', query: { 'path': '' } }, call: (request) => call_docker('GET', `/containers/${request.args.id}/archive`, { query: request.args.query }) },
	// archive extract
	put_archive:  { args: { id: '', query: { 'path': '', 'noOverwriteDirNonDir': '', 'copyUIDGID': '' }, body: '' }, call: (request) => call_docker('PUT', `/containers/${request.args.id}/archive`, { query: request.args.query, payload: request.args.body }) },
	exec:    { args: { id: '', opts: {} }, call: (request) => call_docker('POST', `/containers/${request.args.id}/exec`, { payload: request.args.opts }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/containers/prune', { query: request.args.query }) },

	// Not a docker command - but a local command to invoke ttyd so our browser can open websocket to docker
	ttyd_start: { args: { id: '', cmd: '/bin/sh', port: 7682, uid: '' }, call: (request) => run_ttyd(request) },
};

const image_methods = {
	list:    { args: { query: { 'all': false, 'digests': false, 'shared-size': false, 'manifests': false, 'filters': '' } }, call: (request) => call_docker('GET', '/images/json', { query: request.args.query }) },
	// build is long-running, and will likely cause time-out on the call. Function only here for reference.
	build:   { args: { query: { '': '' }, headers: {} }, call: (request) => call_docker('POST', '/build', { query: request.args.query, headers: request.args.headers }) },
	build_prune: { args: { query: { '': '' }, headers: {} }, call: (request) => call_docker('POST', '/build/prune', { query: request.args.query, headers: request.args.headers }) },
	create:  { args: { query: { '': '' }, headers: {} }, call: (request) => call_docker('POST', '/images/create', { query: request.args.query, headers: request.args.headers }) },
	inspect: { args: { id: '' }, call: (request) => call_docker('GET', `/images/${request.args.id}/json`) },
	history: { args: { id: '' }, call: (request) => call_docker('GET', `/images/${request.args.id}/history`) },
	push:    { args: { name: '', query: { tag: '', platform: '' }, headers: {} }, call: (request) => call_docker('POST', `/images/${request.args.name}/push`, { query: request.args.query, headers: request.args.headers }) },
	tag:     { args: { id: '', query: { 'repo': '', 'tag': '' } }, call: (request) => call_docker('POST', `/images/${request.args.id}/tag`, { query: request.args.query }) },
	remove:  { args: { id: '', query: { 'force': false, 'noprune': false } }, call: (request) => call_docker('DELETE', `/images/${request.args.id}`, { query: request.args.query }) },
	search:  { args: { query: { 'term': '', 'limit': 0, 'filters': '' } }, call: (request) => call_docker('GET', '/images/search', { query: request.args.query }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/images/prune', { query: request.args.query }) },
	// create/commit
	get:     { args: { id: '' }, call: (request) => call_docker('GET', `/images/${request.args.id}/get`) },
	// get == export several
	load:    { args: { query: { 'quiet': false } }, call: (request) => call_docker('POST', '/images/load', { query: request.args.query }) },
};

const network_methods = {
	list:    { args: { query: { 'filters': '' } }, call: (request) => call_docker('GET', '/networks', { query: request.args.query }) },
	inspect: { args: { id: '', query: { 'verbose': false, 'scope': '' } }, call: (request) => call_docker('GET', `/networks/${request.args.id}`, { query: request.args.query }) },
	remove:  { args: { id: '' }, call: (request) => call_docker('DELETE', `/networks/${request.args.id}`) },
	create:  { args: { body: {} }, call: (request) => call_docker('POST', '/networks/create', { payload: request.args.body }) },
	connect: { args: { id: '', body: {} }, call: (request) => call_docker('POST', `/networks/${request.args.id}/connect`, { payload: request.args.body }) },
	disconnect: { args: { id: '', body: {} }, call: (request) => call_docker('POST', `/networks/${request.args.id}/disconnect`, { payload: request.args.body }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/networks/prune', { query: request.args.query }) },
};

const volume_methods = {
	list:    { args: { query: { 'filters': '' } }, call: (request) => call_docker('GET', '/volumes', { query: request.args.query }) },
	create:  { args: { opts: {} }, call: (request) => call_docker('POST', '/volumes/create', { payload: request.args.opts }) },
	inspect: { args: { id: '' }, call: (request) => call_docker('GET', `/volumes/${request.args.id}`) },
	update:  { args: { id: '', query: { 'version': 0 }, spec: {} }, call: (request) => call_docker('PUT', `/volumes/${request.args.id}`, { query: request.args.query, payload: request.args.spec }) },
	remove:  { args: { id: '', query: { 'force': false } }, call: (request) => call_docker('DELETE', `/volumes/${request.args.id}`, { query: request.args.query }) },
	prune:   { args: { query: { 'filters': '' } }, call: (request) => call_docker('POST', '/volumes/prune', { query: request.args.query }) },
};

const methods = {
	'docker': core_methods, 
	'docker.container': container_methods,
	'docker.exec': exec_methods,
	'docker.image': image_methods,
	'docker.network': network_methods,
	'docker.volume': volume_methods,
};

// CLI test mode - check if script is run directly (not loaded by rpcd)
if (caller != 'rpcd') {
	// Usage: ./docker_rpc.uc <object.method> <json-args>
	// Example: ./docker_rpc.uc docker.network.list '{"query":{"filters":""}}'
	// Example: ./docker_rpc.uc docker.image.create '{"query":{"fromImage":"alpine","tag":"latest"}}'
	const scr_name = split(SCRIPT_NAME, '/')[-1] || 'docker_rpc.uc';

	if (length(ARGV) < 1) {
		print(`Usage: ${scr_name} <object.method> [json-args]\n`);

		print("Available methods:\n");
		for (let obj in methods) {
			for (let name, info in methods[obj]) {
				let sig = name;
				if (info && info.args) {
					try {
						sig = `${sig} ${sprintf('\'%J\'', info.args)}`;
					} catch {
						sig = `${sig} <args>`;
					}
				}
				print(`  ${obj}.${sig}\n`);
			}
		}

		print("\nExamples:\n");
		print(`  ${scr_name} docker.version\n`);
		print(`  ${scr_name} docker.network.list '{"query":{}}'\n`);
		print(`  ${scr_name} docker.image.create '{"query":{"fromImage":"alpine","tag":"latest"}}'\n`);
		print(`  ${scr_name} docker.container.list '{"query":{"all":true}}'\n`);
		exit(1);
	}

	const method_path = split(ARGV[0], '.');
	if (length(method_path) < 1) {
		die(`Invalid method path: ${ARGV[0]}\n`);
	}

	// Build object path (e.g., "docker.network")
	const obj_parts = slice(method_path, 0, -1);
	const obj_name = join('.', obj_parts);
	const method_name = method_path[length(method_path) - 1];

	if (!methods[obj_name]) {
		die(`Unknown object: ${obj_name}\n`);
	}

	if (!methods[obj_name][method_name]) {
		die(`Unknown method: ${obj_name}.${method_name}\n`);
	}

	// Parse args if provided
	let args = {};
	if (length(ARGV) > 1) {
		try {
			args = json(ARGV[1]);
		} catch (e) {
			die(`Invalid JSON args: ${e}\n`);
		}
	}

	// Call the method
	const request = { args: args };
	const result = methods[obj_name][method_name].call(request);

	// Pretty print result
	print(result, "\n");
	exit(0);
};

return methods;

```

---

# docker.uc
```ucode
// Docker HTTP streaming endpoint
// Copyright 2025 Paul Donald <newtwen+github@gmail.com>
// Licensed to the public under the Apache License 2.0.
// Built against the docker v1.47 API

'use strict';

import { stdout } from 'fs';
import * as ds from 'luci.docker_socket';
import * as socket from 'socket';
import { cursor } from 'uci';

const BUFF_HEAD = 6; // 8000\r\n
const BUFF_TAIL = 2; // \r\n
const BLOCKSIZE = BUFF_HEAD + 0x8000 + BUFF_TAIL; //sync with Docker chunk size, 32776
// const API_VER = 'v1.47';
const PROTOCOL = 'HTTP/1.1';
const CLIENT_VER = '1';

let DockerController = {

	// Handle file upload for chunked transfer
	handle_file_upload: function(sock) {
		let total_bytes = 0;
		http.setfilehandler(function(meta, chunk, eof) {
			if (meta.file && meta.name === 'upload-archive') {
				if (chunk && length(chunk) > 0) {
					let hex_size = sprintf('%x', length(chunk));
					sock.send(hex_size + '\r\n');
					sock.send(chunk);
					sock.send('\r\n');
					total_bytes += length(chunk);
				}
				if (eof) {
					sock.send('0\r\n\r\n');
				}
			}
		});
		return total_bytes;
	},

	// Reusable header builder
	build_headers: function(headers) {
		let hdrs = [];
		if (headers) {
			for (let key in headers) {
				if (headers[key] != null && headers[key] != '') {
					push(hdrs, `${key}: ${headers[key]}`);
				}
			}
		}
		return length(hdrs) ? join('\r\n', hdrs) : '';
	},

	// Parse the initial HTTP response, split into parts and header lines, and store as properties
	initial_response_parser: function(response_buff) {
		let parts = split(response_buff, /\r?\n\r?\n/, 2);
		let header_lines = split(parts[0], /\r?\n/);
		let status_line = header_lines[0];
		let status_match = match(status_line, /HTTP\/\S+\s+(\d+)/);
		let code = status_match ? int(status_match[1]) : 500;
		this.response_parts = parts;
		this.header_lines = header_lines;
		this.status_line = status_line;
		this.status_match = status_match;
		this.code = code;
	},

	// Stream the rest of the response in chunks from the socket
	stream_response_chunks: function(sock, blocksize) {
		let chunk;
		while ((chunk = sock.recv(blocksize))) {
			if (chunk && length(chunk)) {
				this.debug('Streaming chunk:', substr(chunk, 0, 10));
				stdout.write(chunk);
			}
		}
	},

	// Send a 200 OK response with headers and body
	/* Write CGI response directly to stdout bypassing http.uc
	The minimum to trigger a valid response via CGI is typically
	Status: \r\n

	The Docker response contains the \r\n after its headers, and the browser can
	handle the chunked encoding fine, so we just forward its output verbatim.

	Docker emits a x-docker-container-path-stat header with some meta-data for
	the path, which we forward. uhttpd seems to coalesce headers, and inject its
	own, so we occasionally have two Connection: headers.
	*/
	send_initial_200_response: function(headers, body) {
		stdout.write('Status: 200 OK\r\n');
		if (headers && type(headers) == 'array') {
			stdout.write(join('', headers));
		}

		if (body && index(body, 'HTTP/1.1 200 OK\r\n') === 0) {
			stdout.write(substr(body, length('HTTP/1.1 200 OK\r\n')));
		}
	},

	// Debug output if &debug=... is present
	debug: function(...args) {
		let dbg = http.formvalue('debug');
		let tostr = function(x) { return `${x}`; };
		if (dbg != null && dbg != '') {
			http.prepare_content('application/json');
			http.write_json({msg: join(' ', map(args, tostr)) + '\n' });
		}
	},

	// Generic error response helper
	error_response: function(code, msg, detail) {
		http.status(code ?? 500, msg ?? 'Internal Error');
		http.prepare_content('application/json');
		let out = { error: msg ?? 'Internal Error' };
		if (detail)
			out.detail = detail;
		http.write_json(out);
	},

	get_api_ver: function() {
		let ctx = cursor();
		let version = ctx.get('dockerd', 'globals', 'api_version') || '';
		ctx.unload();
		return version ? `/${version}` : '';
	},

	join_args_array: function(args) {
		return (type(args) == "array") ? join('/', args) : args;
	},

	require_param: function(name) {
		let val = http.formvalue(name);
		if (!val || val == '') die({ code: 400, message: `Missing parameter: ${name}` });
		return val;
	},

	// Reusable query string builder
	build_query_str: function(query_params, skip_keys) {
		let query_str = '';
		if (query_params) {
			let parts = [];
			for (let key in query_params) {
				if (skip_keys && (key in skip_keys))
					continue;
				let val = query_params[key];
				if (val == null || val == '') continue;
				if (type(val) === 'array') {
					for (let v in val) {
						push(parts, `${key}=${v}`);
					}
				} else {
					push(parts, `${key}=${val}`);
				}
			}
			if (length(parts))
				query_str = '?' + join('&', parts);
		}
		return query_str;
	},

	get_archive: function(docker_path, id, docker_function, query_params, archive_name) {
		this.debug('get_archive called', docker_path, id, docker_function, query_params, archive_name);
		id = this.join_args_array(id);
		let id_param = '';
		if (id) id_param = `/${id}`;

		const sock_dest = ds.get_socket_dest_compat();
		const sock = socket.create(sock_dest.family, socket.SOCK_STREAM);

		this.debug('Socket created:', !!sock);

		if (!sock) {
			this.debug('Socket creation failed');
			this.error_response(500, 'Failed to create socket');
			return;
		}

		if (!sock.connect(sock_dest)) {
			this.debug('Socket connect failed');
			sock.close();
			this.error_response(503, 'Failed to connect to Docker daemon');
			return;
		}

		let query_str = type(query_params) === 'object' ? this.build_query_str(query_params) : `?${query_params}`;
		let url = `${docker_path}${id_param}${docker_function}${query_str}`;
		let req = [
			`GET ${this.get_api_ver()}${url} ${PROTOCOL}`,
			`Host: openwrt-docker-ui`,
			`User-Agent: luci-app-dockerman-rpc-ucode/${CLIENT_VER}`,
			`Connection: close`,
			``,
			``
		];

		this.debug('Sending request:', req);
		sock.send(join('\r\n', req));

		let response_buff = sock.recv(BLOCKSIZE);
		this.debug('Received response header block:', response_buff ? substr(response_buff, 0, 100) : 'null');
		if (!response_buff || response_buff == '') {
			this.debug('No response from Docker daemon');
			sock.close();
			this.error_response(500, 'No response from Docker daemon');
			return;
		}

		this.initial_response_parser(response_buff);

		if (this.code != 200) {
			this.debug('Docker error status:', this.code, this.status_line);
			sock.close();
			this.error_response(this.code, 'Docker Error', this.status_line);
			return;
		}

		let filename = length(id) >= 64 ? substr(id, 0, 12) : id;
		if (!filename) filename = 'multi';
		let include_headers = [`Content-Disposition: attachment; filename=\"${filename}_${archive_name}\"\r\n`];

		this.send_initial_200_response(include_headers, response_buff);
		this.stream_response_chunks(sock, BLOCKSIZE);

		sock.close();
		return;
	},

	docker_send: function(method, docker_path, docker_function, query_params, headers, haveFile) {
		this.debug('docker_send called', method, docker_path, docker_function, query_params, headers, haveFile);
		const sock_dest = ds.get_socket_dest_compat();
		const sock = socket.create(sock_dest.family, socket.SOCK_STREAM);

		this.debug('Socket created:', !!sock);

		if (!sock) {
			this.debug('Socket creation failed');
			this.error_response(500, 'Failed to create socket');
			return;
		}

		if (!sock.connect(sock_dest)) {
			this.debug('Socket connect failed');
			sock.close();
			this.error_response(503, 'Failed to connect to Docker daemon');
			return;
		}

		let skip_keys = {
			token: true,
			'X-Registry-Auth': true,
			'upload-name': true,
			'upload-archive': true,
			'upload-path': true,
		};

		let remote = false;

		if (query_params && type(query_params) === 'object' &&
			query_params['remote'] != null && query_params['remote'] != '')
			remote = true;

		let query_str = type(query_params) === 'object' ? this.build_query_str(query_params, skip_keys) : `?${query_params}`;

		let hdr_str = this.build_headers(headers);

		let url = `${docker_path}${docker_function}${query_str}`;

		let req = [
			`${method} ${this.get_api_ver()}${url} ${PROTOCOL}`,
			`Host: openwrt-docker-ui`,
			`User-Agent: luci-app-docker-controller-ucode/${CLIENT_VER}`,
			`Connection: close`,
		];

		if (hdr_str)
			push(req, hdr_str);
		if (haveFile) {
			push(req, 'Content-Type: application/x-tar');
			push(req, 'Transfer-Encoding: chunked');
		}
		push(req, '');
		push(req, '');

		this.debug('Sending request:', req);
		sock.send(join('\r\n', req));

		if (haveFile)
			this.handle_file_upload(sock);
		else
			sock.send('\r\n\r\n');

		let response_buff = sock.recv(BLOCKSIZE);
		this.debug('Received response header block:', response_buff ? substr(response_buff, 0, 100) : 'null');
		if (!response_buff || response_buff == '') {
			this.debug('No response from Docker daemon');
			sock.close();
			this.error_response(500, 'No response from Docker daemon');
			return;
		}

		this.initial_response_parser(response_buff);
		if (this.code != 200) {
			this.debug('Docker error status:', this.code, this.status_line);
			sock.close();
			this.error_response(this.code, 'Docker Error', this.status_line);
			return;
		}

		this.send_initial_200_response('', response_buff);
		this.stream_response_chunks(sock, BLOCKSIZE);
		sock.close();
		return;
	},

	// Handler methods
	container_get_archive: function(id) {
		this.require_param('path');
		this.get_archive('/containers', id, '/archive', http.message.env.QUERY_STRING, 'file_archive.tar');
	},

	container_export: function(id) {
		this.get_archive('/containers', id, '/export', null, 'container_export.tar');
	},

	containers_prune: function() {
		this.docker_send('POST', '/containers', '/prune', http.message.env.QUERY_STRING, {}, false);
	},

	container_put_archive: function(id) {
		this.require_param('path');
		this.docker_send('PUT', '/containers', `/${id}/archive`, http.message.env.QUERY_STRING, {}, true);
	},

	docker_events: function() {
		this.docker_send('GET', '', '/events', http.message.env.QUERY_STRING, {}, false);
	},

	image_build: function(...args) {
		let remote = http.formvalue('remote');
		this.docker_send('POST', '', '/build', http.message.env.QUERY_STRING, {}, !remote);
	},

	image_build_prune: function() {
		this.docker_send('POST', '/build', '/prune', http.message.env.QUERY_STRING, {}, false);
	},

	image_create: function() {
		let headers = {
			'X-Registry-Auth': http.formvalue('X-Registry-Auth'),
		};
		this.docker_send('POST', '/images', '/create', http.message.env.QUERY_STRING, headers, false);
	},

	image_get: function(...args) {
		this.get_archive('/images', args, '/get', http.message.env.QUERY_STRING, 'image_export.tar');
	},

	image_load: function() {
		this.docker_send('POST', '/images', '/load', http.message.env.QUERY_STRING, {}, true);
	},

	images_prune: function() {
		this.docker_send('POST', '/images', '/prune', http.message.env.QUERY_STRING, {}, false);
	},

	image_push: function(...args) {
		let headers = {
			'X-Registry-Auth': http.formvalue('X-Registry-Auth'),
		};
		this.docker_send('POST', `/images/${this.join_args_array(args)}`, '/push', http.message.env.QUERY_STRING, headers, false);
	},

	networks_prune: function() {
		this.docker_send('POST', '/networks', '/prune', http.message.env.QUERY_STRING, {}, false);
	},

	volumes_prune: function() {
		this.docker_send('POST', '/volumes', '/prune', http.message.env.QUERY_STRING, {}, false);
	},
};

// Export all handlers with automatic error wrapping
let controller = DockerController;
let exports = {};
for (let k, v in controller) {
	if (type(v) == 'function')
		exports[k] = v;
}

return exports;

```

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

---

# form.js
```javascript
'use strict';
'require view';
'require form';

// Project code format is tabs, not spaces
return view.extend({
	render: function() {
		let m, s, o;

		/*
		The first argument to form.Map() maps to the configuration file available
		via uci at /etc/config/. In this case, 'example' maps to /etc/config/example.

		If the file is completely empty, the form sections will indicate that the
		section contains no values yet. As such, your package installation (LuCI app
		or software that the app configures) should lay down a basic configuration
		file with all the needed sections.

		The relevant ACL path for reading a configuration with UCI this way is
		read > uci > ["example"]

		The relevant ACL path for writing back the configuration is
		write > uci > ["example"]
		*/
		m = new form.Map('example', _('Example Form'),
			_('Example Form Configuration.'));

		s = m.section(form.TypedSection, 'first', _('first section'));
		s.anonymous = true;

		s.option(form.Value, 'first_option', _('First Option'),
			_('Input for the first option'));

		s = m.section(form.TypedSection, 'second', _('second section'));
		s.anonymous = true;

		o = s.option(form.Flag, 'flag', _('Flag Option'),
			_('A boolean option'));
		o.default = '1';
		o.rmempty = false;

		o = s.option(form.ListValue, 'select', _('Select Option'),
			_('A select option'));
		o.placeholder = 'placeholder';
		o.value('key1', 'value1');
		o.value('key2', 'value2');
		o.rmempty = false;
		o.editable = true;

		s = m.section(form.TypedSection, 'third', _('third section'));
		s.anonymous = true;
		o = s.option(form.Value, 'password_option', _('Password Option'),
			_('Input for a password (storage on disk is not encrypted)'));
		o.password = true;
		o = s.option(form.DynamicList, 'list_option', _('Dynamic list option'));

		return m.render();
	},
});

```

---

# htmlview.js
```javascript
'use strict';
'require uci';
'require view';

return view.extend({
	handleSaveApply: null,
	handleSave: null,
	handleReset: null,
	load: function () {
		return Promise.all([
			// The relevant ACL path for reading a configuration with UCI this way is
			// read > uci > ["example"]
			uci.load('example')
		]);
	},
	render: function (data) {
		var body = E([
			E('h2', _('Example HTML Page'))
		]);
		var sections = uci.sections('example');
		var listContainer = E('div');
		var list = E('ul');
		// Note that this is pretty error-prone, because sections might be missing
		// etcetera.
		list.appendChild(E('li', {
			'class': 'css-class'
		}, ['First Option in first section: ', E('em', {}, [sections[0]
			.first_option])]));
		list.appendChild(E('li', {
			'class': 'css-class'
		}, ['Flag in second section: ', E('em', {}, [sections[1].flag])]));
		list.appendChild(E('li', {
			'class': 'css-class'
		}, ['Select in second section: ', E('em', {}, [sections[1].select])]));
		listContainer.appendChild(list);
		body.appendChild(listContainer);
		console.log(sections);
		return body;
	}
});
```

---

# rpc.js
```javascript
'use strict';
'require form';
'require rpc';
'require view';

/*
Declare the RPC calls that are needed. The object value maps to the name
listed by the shell command

$ ubus list

Custom ucode scripts can be placed in /usr/share/rpcd/ucode, and must emit JSON.

Permissions to make these calls must be granted in /usr/share/rpcd/acl.d
via a file named the same as the application package name (luci-app-example)
*/
const load_sample1 = rpc.declare({
	object: 'luci.example',
	method: 'get_sample1'
});
// Out of the box, this one will be blocked by the framework because there is
// no ACL granting permission.
const load_sample3 = rpc.declare({
	object: 'luci.example',
	method: 'get_sample3'
});


return view.extend({
	generic_failure: function (message) {
		// Map an error message into a div for rendering
		return E('div', {
			'class': 'error'
		}, [_('RPC call failure: '), message])
	},
	render_sample1_using_array: function (sample) {
		console.log('render_sample1_using_array()');
		console.log(sample);
		/*
		Some simple error handling. If the RPC APIs return a JSON structure of the 
		form {"error": "Some error message"} when there's a failure, then the UI
		can check for the presence of the error attribute, and render a failure
		widget instead of breaking completely.
		*/
		if (sample.error) {
			return this.generic_failure(sample.error)
		}

		/*
		Approach 1 for mapping JSON data to a simple table for display. The listing looks
		a bit like key/value pairs, but is actually just an array. The loop logic later
		on must iterate by 2 to get the labels.
		*/
		const fields = [
			_('Cats'), sample.num_cats,
			_('Dogs'), sample.num_dogs,
			_('Parakeets'), sample.num_parakeets,
			_('Should be "Not found"'), sample.not_found,
			_('Is this real?'), sample.is_this_real ? _('Yes') : _('No'),
		];

		/*
		Declare a table element using an automatically available function - E(). E() 
		produces a DOM node, where the first argument is the type of node to produce,
		the second argument is an object of attributes for that node, and the third
		argument is an array of child nodes (which can also be E() calls).
		*/
		var table = E('table', {
			'class': 'table',
			'id': 'approach-1'
		});

		// Loop over the array, starting from index 0. Every even-indexed second element is
		// the label (left column) and the odd-indexed elements are the value (right column)
		for (var i = 0; i < fields.length; i += 2) {
			table.appendChild(
				E('tr', {
					'class': 'tr'
				}, [
					E('td', {
						'class': 'td left',
						'width': '33%'
					}, [fields[i]]),
					E('td', {
						'class': 'td left'
					}, [(fields[i + 1] != null) ? fields[i + 1] : _('Not found')])
				]));
		}
		return table;
	},

	/*
	load() is called on first page load, and the results of each promise are
	placed in an array in the call order. This array is passed to the render()
	function as the first argument.
	*/
	load: function () {
		return Promise.all([
			load_sample1()
		]);
	},
	// render() is called by the LuCI framework to do any data manipulation, and the
	// return is used to modify the DOM that the browser shows.
	render: function (data) {
		// data[0] will be the result from load_sample1
		const sample1 = data[0] || {};

		// Render the tables as individual sections.
		return E('div', {}, [
			E('div', {
				'class': 'cbi-section warning'
			}, _('See browser console for raw data')),
			E('div', {
				'class': 'cbi-map',
				'id': 'map'
			}, [
				E('div', {
					'class': 'cbi-section',
					'id': 'cbi-sample-js'
				}, [
					E('div', {
						'class': 'left'
					}, [
						// _() notation on strings is used for translation detection
						E('h3', _('Sample JS via RPC')),
						E('div', {}), _(
							"JSON converted to table via array building and loop"
							),
						this.render_sample1_using_array(sample1)
					]),
				]),
			]),
		]);
	},
	/*
	Since this is a view-only screen, the handlers are disabled
	Normally, when using something like Map or JSONMap, you would 
	not null out these handlers, so that the form can be saved/applied.
    
	With a RPC data source, you would need to define custom handlers
	that verify the changes, and make RPC calls to a backend that can
	process the request.
	*/
	handleSave: null,
	handleSaveApply: null,
	handleReset: null
})
```

---

# rpc-jsonmap-tablesection.js
```javascript
'use strict';
'require form';
'require rpc';
'require view';

/*
Declare the RPC calls that are needed. The object value maps to the name
listed by the shell command

$ ubus list

Custom ucode scripts can be placed in /usr/share/rpcd/ucode, and must emit JSON.

Permissions to make these calls must be granted in /usr/share/rpcd/acl.d
via a file named the same as the application package name (luci-app-example)
*/
const load_sample2 = rpc.declare({
	object: 'luci.example',
	method: 'get_sample2'
});

function capitalize(message) {
	var arr = message.split(" ");
	for (var i = 0; i < arr.length; i++) {
		arr[i] = arr[i].charAt(0).toUpperCase() + arr[i].slice(1);
	}
	return arr.join(" ");
}

return view.extend({
	generic_failure: function (message) {
		// Map an error message into a div for rendering
		return E('div', {
			'class': 'error'
		}, [_('RPC call failure: '), message])
	},
	render_sample2_using_jsonmap: function (sample) {
		console.log('render_sample2_using_jsonmap()');
		console.log(sample);

		// Handle errors as before
		if (sample.error) {
			return this.generic_failure(sample.error)
		}

		// Variables you'll usually see declared in LuCI JS apps; forM, Section, Option
		let m, s, o;

		/*
		LuCI has the concept of a JSONMap. This will map a structured object to
		a configuration form. Normally you'd use this with a UCI-powered result,
		since saving via an RPC call is going to be more difficult than using the
		built-in UCI/ubus libraries.
        
		https://openwrt.github.io/luci/jsapi/LuCI.form.JSONMap.html
        
		Execute   ubus call luci.example get_sample2   to see the JSON being used.
		*/
		m = new form.JSONMap(sample, _('JSONMap TableSection Sample'), _(
			'See browser console for raw data'));
		// Make the form read-only; this only matters if the apply/save/reset handlers
		// are not replaced with null to disable them.
		m.readonly = true;
		// Set up for a tabbed display
		m.tabbed = false;

		const option_names = Object.keys(sample);
		for (var i = option_names.length - 1; i >= 0; i--) {
			var option_name = option_names[i];
			var display_name = option_name.replace("_", " ");
			s = m.section(form.TableSection, option_name, capitalize(display_name), _(
				'Description for this table section'))
			o = s.option(form.Value, 'name', _('Option name'));
			o = s.option(form.Value, 'value', _('Option value'));
			o = s.option(form.DynamicList, 'parakeets', 'Parakeets');
		}
		return m;
	},
	/*
	load() is called on first page load, and the results of each promise are
	placed in an array in the call order. This array is passed to the render()
	function as the first argument.
	*/
	load: function () {
		return Promise.all([
			load_sample2(),
		]);
	},
	// render() is called by the LuCI framework to do any data manipulation, and the
	// return is used to modify the DOM that the browser shows.
	render: function (data) {
		// data[0] will be the result from load_sample2
		var sample2 = data[0] || {};
		return this.render_sample2_using_jsonmap(sample2).render();
	},
	/*
	Since this is a view-only screen, the handlers are disabled
	Normally, when using something like Map or JSONMap, you would 
	not null out these handlers, so that the form can be saved/applied.
    
	With a RPC data source, you would need to define custom handlers
	that verify the changes, and make RPC calls to a backend that can
	process the request.
	*/
	handleSave: null,
	handleSaveApply: null,
	handleReset: null
})
```

---

# rpc-jsonmap-typedsection.js
```javascript
'use strict';
'require form';
'require rpc';
'require view';

/*
Declare the RPC calls that are needed. The object value maps to the name
listed by the shell command

$ ubus list

Custom ucode scripts can be placed in /usr/share/rpcd/ucode, and must emit JSON.

Permissions to make these calls must be granted in /usr/share/rpcd/acl.d
via a file named the same as the application package name (luci-app-example)
*/
const load_sample2 = rpc.declare({
	object: 'luci.example',
	method: 'get_sample2'
});

function capitalize(message) {
	var arr = message.split(" ");
	for (var i = 0; i < arr.length; i++) {
		arr[i] = arr[i].charAt(0).toUpperCase() + arr[i].slice(1);
	}
	return arr.join(" ");
}

return view.extend({
	generic_failure: function (message) {
		// Map an error message into a div for rendering
		return E('div', {
			'class': 'error'
		}, [_('RPC call failure: '), message])
	},
	render_sample2_using_jsonmap: function (sample) {
		console.log('render_sample2_using_jsonmap()');
		console.log(sample);

		// Handle errors as before
		if (sample.error) {
			return this.generic_failure(sample.error)
		}

		// Variables you'll usually see declared in LuCI JS apps; forM, Section, Option
		let m, s, o;

		/*
		LuCI has the concept of a JSONMap. This will map a structured object to
		a configuration form. Normally you'd use this with a UCI-powered result,
		since saving via an RPC call is going to be more difficult than using the
		built-in UCI/ubus libraries.
        
		https://openwrt.github.io/luci/jsapi/LuCI.form.JSONMap.html
        
		Execute   ubus call luci.example get_sample2   to see the JSON being used.
		*/
		m = new form.JSONMap(sample, _('JSONMap TypedSection Sample'), _(
			'See browser console for raw data'));
		// Make the form read-only; this only matters if the apply/save/reset handlers
		// are not replaced with null to disable them.
		m.readonly = true;
		// Set up for a tabbed display
		m.tabbed = true;

		const option_names = Object.keys(sample);
		for (var i = option_names.length - 1; i >= 0; i--) {
			var option_name = option_names[i];
			var display_name = option_name.replace("_", " ");
			s = m.section(form.TypedSection, option_name, capitalize(display_name), _(
				'Description for this typed section'))
			o = s.option(form.Value, 'name', _('Option name'));
			o = s.option(form.Value, 'value', _('Option value'));
			o = s.option(form.DynamicList, 'parakeets', 'Parakeets');
		}
		return m;
	},
	/*
	load() is called on first page load, and the results of each promise are
	placed in an array in the call order. This array is passed to the render()
	function as the first argument.
	*/
	load: function () {
		return Promise.all([
			load_sample2(),
		]);
	},
	// render() is called by the LuCI framework to do any data manipulation, and the
	// return is used to modify the DOM that the browser shows.
	render: function (data) {
		// data[0] will be the result from load_sample2
		var sample2 = data[0] || {};
		return this.render_sample2_using_jsonmap(sample2).render();
	},
	/*
	Since this is a view-only screen, the handlers are disabled
	Normally, when using something like Map or JSONMap, you would 
	not null out these handlers, so that the form can be saved/applied.
    
	With a RPC data source, you would need to define custom handlers
	that verify the changes, and make RPC calls to a backend that can
	process the request.
	*/
	handleSave: null,
	handleSaveApply: null,
	handleReset: null
})
```
