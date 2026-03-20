---
title: 'ucode module: log'
module: ucode
origin_type: c_source
token_count: 5098
version: 3d482fb
source_file: L1-raw/ucode/c_source-api-module-log.md
last_pipeline_run: '2026-03-20T01:28:00.439321+00:00'
upstream_path: lib/log.c
language: c
ai_summary: Provides syslog integration for ucode scripts via the POSIX syslog API. Exposes openlog(), syslog(), and closelog() with facility constants (LOG_DAEMON, LOG_USER, LOG_LOCAL0–LOG_LOCAL7) and priority constants (LOG_DEBUG, LOG_INFO, LOG_NOTICE, LOG_WARNING, LOG_ERR, LOG_CRIT). Enables structured kernel-level log emission from ucode services.
ai_when_to_use: Use in ucode daemons and init handlers to emit structured syslog entries that appear in OpenWrt's logread output alongside other system services, rather than writing to stdout or a plain file.
ai_related_topics:
- log.openlog
- log.syslog
- log.closelog
- LOG_DAEMON
- LOG_INFO
- LOG_ERR
---
# ucode module: log

> **Live docs:** https://ucode.mein.io/module-log.html

---

## System logging functions

The `log` module provides bindings to the POSIX syslog functions `openlog()`,
`syslog()` and `closelog()` as well as - when available - the OpenWrt
specific ulog library functions.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import { openlog, syslog, LOG_PID, LOG_USER, LOG_ERR } from 'log';

  openlog("my-log-ident", LOG_PID, LOG_USER);
  syslog(LOG_ERR, "An error occurred!");

  // OpenWrt specific ulog functions
  import { ulog_open, ulog, ULOG_SYSLOG, LOG_DAEMON, LOG_INFO } from 'log';

  ulog_open(ULOG_SYSLOG, LOG_DAEMON, "my-log-ident");
  ulog(LOG_INFO, "The current epoch is %d", time());
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as log from 'log';

  log.openlog("my-log-ident", log.LOG_PID, log.LOG_USER);
  log.syslog(log.LOG_ERR, "An error occurred!");

  // OpenWrt specific ulog functions
  log.ulog_open(log.ULOG_SYSLOG, log.LOG_DAEMON, "my-log-ident");
  log.ulog(log.LOG_INFO, "The current epoch is %d", time());
  ```

Additionally, the log module namespace may also be imported by invoking the
`ucode` interpreter with the `-llog` switch.

## Constants

The `log` module declares a number of numeric constants to specify logging
facility, priority and option values, as well as ulog specific channels.

### Syslog Options

| Constant Name | Description                                             |
|---------------|---------------------------------------------------------|
| `LOG_PID`     | Include PID with each message.                          |
| `LOG_CONS`    | Log to console if error occurs while sending to syslog. |
| `LOG_NDELAY`  | Open the connection to the logger immediately.          |
| `LOG_ODELAY`  | Delay open until the first message is logged.           |
| `LOG_NOWAIT`  | Do not wait for child processes created during logging. |

### Syslog Facilities

| Constant Name  | Description                                      |
|----------------|--------------------------------------------------|
| `LOG_AUTH`     | Authentication/authorization messages.           |
| `LOG_AUTHPRIV` | Private authentication messages.                 |
| `LOG_CRON`     | Clock daemon (cron and at commands).             |
| `LOG_DAEMON`   | System daemons without separate facility values. |
| `LOG_FTP`      | FTP server daemon.                               |
| `LOG_KERN`     | Kernel messages.                                 |
| `LOG_LPR`      | Line printer subsystem.                          |
| `LOG_MAIL`     | Mail system.                                     |
| `LOG_NEWS`     | Network news subsystem.                          |
| `LOG_SYSLOG`   | Messages generated internally by syslogd.        |
| `LOG_USER`     | Generic user-level messages.                     |
| `LOG_UUCP`     | UUCP subsystem.                                  |
| `LOG_LOCAL0`   | Local use 0 (custom facility).                   |
| `LOG_LOCAL1`   | Local use 1 (custom facility).                   |
| `LOG_LOCAL2`   | Local use 2 (custom facility).                   |
| `LOG_LOCAL3`   | Local use 3 (custom facility).                   |
| `LOG_LOCAL4`   | Local use 4 (custom facility).                   |
| `LOG_LOCAL5`   | Local use 5 (custom facility).                   |
| `LOG_LOCAL6`   | Local use 6 (custom facility).                   |
| `LOG_LOCAL7`   | Local use 7 (custom facility).                   |

### Syslog Priorities

| Constant Name | Description                         |
|---------------|-------------------------------------|
| `LOG_EMERG`   | System is unusable.                 |
| `LOG_ALERT`   | Action must be taken immediately.   |
| `LOG_CRIT`    | Critical conditions.                |
| `LOG_ERR`     | Error conditions.                   |
| `LOG_WARNING` | Warning conditions.                 |
| `LOG_NOTICE`  | Normal, but significant, condition. |
| `LOG_INFO`    | Informational message.              |
| `LOG_DEBUG`   | Debug-level message.                |

### Ulog channels

| Constant Name | Description                          |
|---------------|--------------------------------------|
| `ULOG_KMSG`   | Log messages to `/dev/kmsg` (dmesg). |
| `ULOG_STDIO`  | Log messages to stdout.              |
| `ULOG_SYSLOG` | Log messages to syslog.              |

### log.openlog([ident], [options], [facility]) ⇒ `boolean`
Open connection to system logger.

The `openlog()` function instructs the program to establish a connection to
the system log service and configures the default facility and identification
for use in subsequent log operations. It may be omitted, in which case the
first call to `syslog()` will implicitly call `openlog()` with a default
ident value representing the program name and a default `LOG_USER` facility.

The log option argument may be either a single string value containing an
option name, an array of option name strings or a numeric value representing
a bitmask of `LOG_*` option constants.

The facility argument may be either a single string value containing a
facility name or one of the numeric `LOG_*` facility constants in the module
namespace.

Returns `true` if the system `openlog()` function was invoked.

Returns `false` if an invalid argument, such as an unrecognized option or
facility name, was provided.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| [ident] | `string` |  | A string identifying the program name. If omitted, the name of the calling process is used by default. |
| [options] | `number` \| [`LogOption`](#module_log.LogOption) \| [`Array.<LogOption>`](#module_log.LogOption) |  | Logging options to use. See [LogOption](#module_log.LogOption) for recognized option names. |
| [facility] | `number` \| [`LogFacility`](#module_log.LogFacility) | `"user"` | The facility to use for log messages generated by subsequent syslog calls. See [LogFacility](#module_log.LogFacility) for recognized facility names. |

**Example**  
```ucode
// Example usage of openlog function
openlog("myapp", LOG_PID | LOG_NDELAY, LOG_LOCAL0);

// Using option names instead of bitmask and LOG_USER facility
openlog("myapp", [ "pid", "ndelay" ], "user");
```

### log.syslog(priority, format, [...args]) ⇒ `boolean`
Log a message to the system logger.

This function logs a message to the system logger. The function behaves in a
sprintf-like manner, allowing the use of format strings and associated
arguments to construct log messages.

If the `openlog` function has not been called explicitly before, `syslog()`
implicitly calls `openlog()`, using a default ident and `LOG_USER` facility
value before logging the message.

If the `format` argument is not a string and not `null`, it will be
implicitly converted to a string and logged as-is, without further format
string processing.

Returns `true` if a message was passed to the system `syslog()` function.

Returns `false` if an invalid priority value or an empty message was given.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| priority | `number` \| [`LogPriority`](#module_log.LogPriority) | Log message priority. May be either a number value (potentially bitwise OR-ed with a log facility constant) which is passed as-is to the system `syslog()` function or a priority name string. See [LogPriority](#module_log.LogPriority) for recognized priority names. |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
// Example usage of syslog function with format string and arguments
const username = "user123";
const errorCode = 404;
syslog(LOG_ERR, "User %s encountered error: %d", username, errorCode);

// If openlog has not been called explicitly, it is implicitly called with defaults:
syslog(LOG_INFO, "This message will be logged with default settings.");

// Selectively override used facility by OR-ing numeric constant
const password =" secret";
syslog(LOG_DEBUG|LOG_AUTHPRIV, "The password %s has been wrong", secret);

// Using priority names for logging
syslog("emerg", "System shutdown imminent!");

// Implicit stringification
syslog("debug", { foo: 1, bar: true, baz: [1, 2, 3] });
```

### log.closelog()
Close connection to system logger.

The usage of this function is optional, and usually an explicit log
connection tear down is not required.

**Kind**: instance method of [`log`](#module_log)  

### log.ulog\_open([channel], [facility], [ident]) ⇒ `boolean`
Configure ulog logger.

This functions configures the ulog mechanism and is analogeous to using the
`openlog()` function in conjuncton with `syslog()`.

The `ulog_open()` function is OpenWrt specific and may not be present on
other systems. Use `openlog()` and `syslog()` instead for portability to
non-OpenWrt environments.

A program may use multiple channels to simultaneously output messages using
different means. The channel argument may either be a single string value
containing a channel name, an array of channel names or a numeric value
representing a bitmask of `ULOG_*` channel constants.

The facility argument may be either a single string value containing a
facility name or one of the numeric `LOG_*` facility constants in the module
namespace.

The default facility value varies, depending on the execution context of the
program. In OpenWrt's preinit boot phase, or when stdout is not connected to
an interactive terminal, the facility defaults to `"daemon"` (`LOG_DAEMON`),
otherwise to `"user"` (`LOG_USER`).

Likewise, the default channel is selected depending on the context. During
OpenWrt's preinit boot phase, the `"kmsg"` channel is used, for interactive
terminals the `"stdio"` one and for all other cases the `"syslog"` channel
is selected.

Returns `true` if ulog was configured.

Returns `false` if an invalid argument, such as an unrecognized channel or
facility name, was provided.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| [channel] | `number` \| [`UlogChannel`](#module_log.UlogChannel) \| [`Array.<UlogChannel>`](#module_log.UlogChannel) | Specifies the log channels to use. See [UlogChannel](#module_log.UlogChannel) for recognized channel names. |
| [facility] | `number` \| [`LogFacility`](#module_log.LogFacility) | The facility to use for log messages generated by subsequent `ulog()` calls. See [LogFacility](#module_log.LogFacility) for recognized facility names. |
| [ident] | `string` | A string identifying the program name. If omitted, the name of the calling process is used by default. |

**Example**  
```ucode
// Log to dmesg and stderr
ulog_open(["stdio", "kmsg"], "daemon", "my-program");

// Use numeric constants and use implicit default ident
ulog_open(ULOG_SYSLOG, LOG_LOCAL0);
```

### log.ulog(priority, format, [...args]) ⇒ `boolean`
Log a message via the ulog mechanism.

The `ulog()` function outputs the given log message to all configured ulog
channels unless the given priority level exceeds the globally configured ulog
priority threshold. See [ulog_threshold()](#module_log+ulog_threshold)
for details.

The `ulog()` function is OpenWrt specific and may not be present on other
systems. Use `syslog()` instead for portability to non-OpenWrt environments.

Like `syslog()`, the function behaves in a sprintf-like manner, allowing the
use of format strings and associated arguments to construct log messages.

If the `ulog_open()` function has not been called explicitly before, `ulog()`
implicitly configures certain defaults, see
[ulog_open()](#module_log+ulog_open) for a detailled description.

If the `format` argument is not a string and not `null`, it will be
implicitly converted to a string and logged as-is, without further format
string processing.

Returns `true` if a message was passed to the underlying `ulog()` function.

Returns `false` if an invalid priority value or an empty message was given.

**Kind**: instance method of [`log`](#module_log)  
**See**

- module:log#ulog_open
- module:log#ulog_threshold
- module:log#syslog

| Param | Type | Description |
| --- | --- | --- |
| priority | `number` \| [`LogPriority`](#module_log.LogPriority) | Log message priority. May be either a number value or a priority name string. See [LogPriority](#module_log.LogPriority) for recognized priority names. |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
// Example usage of ulog function with format string and arguments
const username = "user123";
const errorCode = 404;
ulog(LOG_ERR, "User %s encountered error: %d", username, errorCode);

// Using priority names for logging
ulog("err", "General error encountered");

// Implicit stringification
ulog("debug", { foo: 1, bar: true, baz: [1, 2, 3] });
```

### log.ulog\_close()
Close ulog logger.

Resets the ulog channels, the default facility and the log ident value to
defaults.

In case the `"syslog"` channel has been configured, the underlying
`closelog()` function will be invoked.

The usage of this function is optional, and usually an explicit ulog teardown
is not required.

The `ulog_close()` function is OpenWrt specific and may not be present on
other systems. Use `closelog()` in conjunction with `syslog()` instead for
portability to non-OpenWrt environments.

**Kind**: instance method of [`log`](#module_log)  
**See**: module:log#closelog  

### log.ulog\_threshold([priority]) ⇒ `boolean`
Set ulog priority threshold.

This function configures the application wide log message threshold for log
messages emitted with `ulog()`. Any message with a priority higher (= less
severe) than the threshold priority will be discarded. This is useful to
implement application wide verbosity settings without having to wrap `ulog()`
invocations into a helper function or guarding code.

When no explicit threshold has been set, `LOG_DEBUG` is used by default,
allowing log messages with all known priorities.

The `ulog_threshold()` function is OpenWrt specific and may not be present on
other systems. There is no syslog equivalent to this ulog specific threshold
mechanism.

The priority argument may be either a string value containing a priority name
or one of the numeric `LOG_*` priority constants in the module namespace.

Returns `true` if a threshold was set.

Returns `false` if an invalid priority value was given.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| [priority] | `number` \| [`LogPriority`](#module_log.LogPriority) | The priority threshold to configure. See [LogPriority](#module_log.LogPriority) for recognized priority names. |

**Example**  
```ucode
// Set threshold to "warning" or more severe
ulog_threshold(LOG_WARNING);

// This message will be supressed
ulog(LOG_DEBUG, "Testing thresholds");

// Using priority name
ulog_threshold("debug");
```

### log.INFO(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_INFO.

This function is convenience wrapper for `ulog(LOG_INFO, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
INFO("This is an info log message");
```

### log.NOTE(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_NOTICE.

This function is convenience wrapper for `ulog(LOG_NOTICE, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
NOTE("This is a notification log message");
```

### log.WARN(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_WARNING.

This function is convenience wrapper for `ulog(LOG_WARNING, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
WARN("This is a warning");
```

### log.ERR(format, [...args]) ⇒ `boolean`
Invoke ulog with LOG_ERR.

This function is convenience wrapper for `ulog(LOG_ERR, ...)`.

See [ulog()](#module_log+ulog) for details.

**Kind**: instance method of [`log`](#module_log)  

| Param | Type | Description |
| --- | --- | --- |
| format | `\*` | The sprintf-like format string for the log message, or any other, non-null, non-string value type which will be implicitly stringified and logged as-is. |
| [...args] | `\*` | In case a format string value was provided in the previous argument, then all subsequent arguments are used to replace the placeholders in the format string. |

**Example**  
```ucode
ERR("This is an error!");
```

### log.LogOption : `enum`
The following log option strings are recognized:

| Log Option | Description                                                |
|------------|------------------------------------------------------------|
| `"pid"`    | Include PID with each message.                             |
| `"cons"`   | Log to console if an error occurs while sending to syslog. |
| `"ndelay"` | Open the connection to the logger immediately.             |
| `"odelay"` | Delay open until the first message is logged.              |
| `"nowait"` | Do not wait for child processes created during logging.    |

**Kind**: static enum of [`log`](#module_log)  

### log.LogFacility : `enum`
The following log facility strings are recognized:

| Facility     | Description                                      |
|--------------|--------------------------------------------------|
| `"auth"`     | Authentication/authorization messages.           |
| `"authpriv"` | Private authentication messages.                 |
| `"cron"`     | Clock daemon (cron and at commands).             |
| `"daemon"`   | System daemons without separate facility values. |
| `"ftp"`      | FTP server daemon.                               |
| `"kern"`     | Kernel messages.                                 |
| `"lpr"`      | Line printer subsystem.                          |
| `"mail"`     | Mail system.                                     |
| `"news"`     | Network news subsystem.                          |
| `"syslog"`   | Messages generated internally by syslogd.        |
| `"user"`     | Generic user-level messages.                     |
| `"uucp"`     | UUCP subsystem.                                  |
| `"local0"`   | Local use 0 (custom facility).                   |
| `"local1"`   | Local use 1 (custom facility).                   |
| `"local2"`   | Local use 2 (custom facility).                   |
| `"local3"`   | Local use 3 (custom facility).                   |
| `"local4"`   | Local use 4 (custom facility).                   |
| `"local5"`   | Local use 5 (custom facility).                   |
| `"local6"`   | Local use 6 (custom facility).                   |
| `"local7"`   | Local use 7 (custom facility).                   |

**Kind**: static enum of [`log`](#module_log)  

### log.LogPriority : `enum`
The following log priority strings are recognized:

| Priority    | Description                         |
|-------------|-------------------------------------|
| `"emerg"`   | System is unusable.                 |
| `"alert"`   | Action must be taken immediately.   |
| `"crit"`    | Critical conditions.                |
| `"err"`     | Error conditions.                   |
| `"warning"` | Warning conditions.                 |
| `"notice"`  | Normal, but significant, condition. |
| `"info"`    | Informational message.              |
| `"debug"`   | Debug-level message.                |

**Kind**: static enum of [`log`](#module_log)  

### log.UlogChannel : `enum`
The following ulog channel strings are recognized:

| Channel    | Description                                       |
|------------|---------------------------------------------------|
| `"kmsg"`   | Log to `/dev/kmsg`, log messages appear in dmesg. |
| `"syslog"` | Use standard `syslog()` mechanism.                |
| `"stdio"`  | Use stderr for log output.                        |

**Kind**: static enum of [`log`](#module_log)
