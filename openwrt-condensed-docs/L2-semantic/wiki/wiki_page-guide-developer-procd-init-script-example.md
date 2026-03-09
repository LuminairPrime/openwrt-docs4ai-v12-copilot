---
title: Create a sample procd init script
module: wiki
origin_type: wiki_page
token_count: 2417
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-procd-init-script-example.md
last_pipeline_run: '2026-03-09T17:28:41.757217+00:00'
language: text
---
# Create a sample procd init script

\<WRAP center round info 80%\> This article is a mostly verbatim copy of [this archived article](https://web.archive.org/web/20220518121856/https://joostoostdijk.com/posts/service-configuration-with-procd), all credit goes to the original author, **Joost Oostdijk**  
It was adapted to use an equivalent shell script instead of NodeJS JavaScript, because it's lighter and better for a simple testing setup on most OpenWrt devices. \</WRAP\>

Procd init scripts gives us many nice to use features by default such as a restart strategy and the ability to store and read configuration from the UCI system.

## Setting up

As example, lets say we’d want to create shell script as a service and that this service can be configured with a message and a timeout in order for us to be reminded to get up from ur desks once in a while. Our service name will be myservice and it depends on the following script

``` bash
#!/bin/sh

#these if statements will check input and place default values if no input is given
#they will also check if input is a number so you can call 
#this script with just a time and it will still work correctly

if [ "$1" = '' ]; then
    name="You"
else
    if echo "$1" | egrep -q '^[0-9]+$'; then
        name="You"
    else
        name="$1"
    fi
fi

if [ "$2" = '' ]; then
    every="5"
else
    every="$2"
fi

if echo "$1" | egrep -q '^[0-9]+$'; then
    every="$1"
fi

#endless loop, will print the message every X seconds as indicated in the $every variable

while [ 1 ]; do 
    echo "Hey, $name, it's time to get up"
    sleep $every
done

exit 0

```

Place it in **/var/myscript.sh** and test it by running on OpenWrt

    $ /bin/sh /var/myscript.sh "Name Surname"

## Creating a basic procd script

Now that we have a working script, we can make a service out of it. Create a file in /etc/init.d/myservice with the following content

``` bash
#!/bin/sh /etc/rc.common
USE_PROCD=1
START=95
STOP=01
start_service() {
    procd_open_instance
    procd_set_param command /bin/sh "/var/myscript.sh"
    procd_close_instance
}
```

First, it includes the common ‘run commands’ file /etc/rc.common needed for a service. This file defines several functions that can be used to manage the service lifecycle, it supports old style init scripts as well as procd scripts. In order to tell that we want to use the new style we then set the USE_PROCD flag.

The START option basically tell the system when the service should start and stop during startup and shutdown of OpenWrt.

This init script isn’t very useful at the moment but it shows the basic building blocks on which we will develop the script further.

## Enabling the service

To tell OpenWrt that we have a new service we would need to run

\<code\> /etc/init.d/myservice enable\</code\>

This will install a symlink for us in directory /etc/rc.d/ called S95myservice (because `START=95`) which points to our respective service script in /etc/init.d/. OpenWrt will start the services according the the order of S\* scripts in /etc/rc.d/. To see the order you could simply run

    $ ls -la /etc/rc.d/S*

...

It is useful to be able to influence the order of startup of services, if our service would be dependent on the network we’d make sure that the START sequence ‘index’ is at least 1 more than the START sequence of the network service.

The same rules apply for the optional STOP parameters, only this time it defines in which order the services will be shutdown. To see Which shutdown scripts are activated you can run

    $ ls -la /etc/rc.d/K*

You always need to define a START or STOP sequence in your script (you can also define both). If you define a STOP sequence you also want to define a stop_service() handler in the init script. This handler is usually taking care of cleaning up service resources or persistence of data needed when the service starts again. Testing the service

Finally, lets just test our service. Open a second shell to the OpenWrt device and run

    $ logread -f

This will tail the system logs on the device. then enable (if you havent done that yet), and start the service.

    $ /etc/init.d/myservice enable
    $ /etc/init.d/myservice start

After about 5 seconds we should see the message repeat itself in the log, but we didn’t… We still need to redirect stdout and stderr to logd in order to see the console.log output in the system logs.

``` bash
#!/bin/sh /etc/rc.common

USE_PROCD=1

START=95
STOP=01

start_service() {
    procd_open_instance
    procd_set_param command /bin/sh "/var/myscript.sh"
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}
```

Now, when we restart we should see something like

    $ logread -f
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ...

Setting up a service simple script like above with procd already gives us some advantages

\* Common api to manage services \* The service will automatically start at every boot

## Service configuration

It’s time to get more personal, and to that we will use OpenWrts UCI configuration interface. Create a configuration file /etc/config/myservice with the following content

    config myservice 'hello'
        option name 'Joost'
        option every '5'

UCI will immediately pick this up and the config for our service can be inspected like

    $ uci show myservice
    myservice.hello=myservice
    myservice.hello.name=Joost
    myservice.hello.every='5'

Also single options can be requested

    $ uci get myservice.hello.name

and we can also change specific configuration with UCI

    $ uci set myservice.hello.name=Knight
    $ uci commit

Now, we’ll introduce a couple of changes to the service script in order to read and use the configuration in our script.

## Loading service configuration

We can already pass configuration to the node script by passing arguments to it. The only thing we need to do is load the services matching configuration, store the values of the options we need into some variables and pass them into the command that starts the script.

``` bash
#!/bin/sh /etc/rc.common

USE_PROCD=1

START=95
STOP=01

CONFIGURATION=myservice

start_service() {
    # Reading config
    config_load "${CONFIGURATION}"
    local name
    local every

    config_get name hello name
    config_get every hello every

    procd_open_instance

    # pass config to script on start
    procd_set_param command /bin/sh "/var/myscript.sh" "$name" "$every"
    procd_set_param file /etc/config/myservice
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}
```

We can pass new configuration by running

    $ uci set myservice.hello.name=Woodrow Wilson Smith
    $ uci commit

Note that in the service script the arguments are quoted, which allows us to use spaces in the name option. If we wouldn’t do this, each part of the name would be treated as a separate argument.

Apart from the loading and passing of config to our script we also added

    ...
    procd_set_param file /etc/config/myservice
    ...

With that line in place we are able to restart the service whenever only our configuration has changed.

    $ /etc/init.d/myservice reload

## Advanced options

There are a couple of more options that can be configured in a procd scripts ‘instance block’ that might be handy to know about. I’ll list a few here, but this is by no means covering everything.

- **respawn**  
  respawn your service automatically when it terminates for some reason.  
  `procd_set_param respawn \
        ${respawn_threshold:-3600} \
        ${respawn_timeout:-5} ${respawn_retry:-5}`  
  In this example we respawn if process terminates sooner than respawn_threshold, it is considered crashed and after 5 retries the service is stopped. However, if it terminates later than respawn_threshold, it would be respawned indefinitely.

<!-- -->

- **pidfile**  
  Configure where to store the pid file  
  `procd_set_param pidfile $PIDFILE`

<!-- -->

- **env vars**  
  Pass environment variables to your process with  
  `procd_set_param env A_VAR=avalue`

<!-- -->

- **ulimit**  
  If you need to set resource limits for your process you can use  
  `procd_set_param limits core="unlimited"`  
  To see the system wide settings for ulimt on an OpenWrt device you can run  
  `$ ulimit -a
  -f: file size (blocks)             unlimited
  -t: cpu time (seconds)             unlimited
  -d: data seg size (kb)             unlimited
  -s: stack size (kb)                8192
  -c: core file size (blocks)        0
  -m: resident set size (kb)         unlimited
  -l: locked memory (kb)             64
  -p: processes                      475
  -n: file descriptors               1024
  -v: address space (kb)             unlimited
  -w: locks                          unlimited
  -e: scheduling priority            0
  -r: real-time priority             0
  `
- **user**  
  To change the user that runs the service you can use  
  \<code\> procd_set_param user nobody \</code\>  
  Default OpenWrt only has a ‘root’ user or ‘nobody’ as the process owner.  
  You can add users with the usual linux way, see [Create a non-privileged user in OpenWrt](/docs/guide-user/security/secure.access#create_a_non-privileged_user_in_openwrt) or if you are creating an actual package you can use [buildpackage defines](/docs/guide-developer/packages#buildpackage_defines) to make OpenWrt generate the user when the package is installed.