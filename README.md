consoled
========

A config-based abstraction over coreos/fleet

What is consoled?
-----------------

Consoled is a command line tool that provides a way to generate systemd service units from a config file. These services then can be submitted and started on a CoreOS cluster. Technically, this will work on any cluster running fleet and docker. But seriously, use CoreOS. ;)

Dependencies
------------

As of now, consoled is just a make tool. No real dependency is required except for python.

Config
------

The config is a YAML or JSON file that defines different things about the environment. Here's an example in YAML:

```yml
containers:

  hipache: quarry/hipache

  web:
    image: registry.myapp.com:5000/myapp/web
    requires:
      - redis
    endpoints:
      - redis-instance

  redis:
    image: dockerfiles/redis
    volumes:
      /redis-data: /media/state/redis-data


services:

  load-balancing:
    hipache:
      endpoints:
        - web-service

  web-service:
    - web


instances:
  redis-instance: redis


scale:
  load-balancing: 2
  web-service: 20


hosts:
  "flavor:performance-2":
    - redis-instance
  "flavor:standard-1gb":
    - web-service
    - load-balancing
```

#### Containers

```yml
containers:

  hipache: quarry/hipache

  web:
    image: registry.myapp.com:5000/myapp/web
    requires:
      - redis
    endpoints:
      - redis-instance

  redis:
    image: dockerfiles/redis
    volumes:
      /redis-data: /media/state/redis-data
```

A Container names a docker image and provides context when running that image. The following options can be used to configure how a container runs.

- `image`: Defines an image that can be hosted on docker's public index or on your own registry. The image must be able to be pulled from anywhere in the cluster.
- `requires`: A list of other containers to link using docker's `-link`. Since required containers will be started before the parent container, a container cannot directly or indirectly require itself. You can require containers that require other containers, and consoled will resolve and manage the dependencies at runtime for you. When containers are linked, the container name is used as the link alias. If identical containers are linked, the link alias will increment.

If the following requires are used:

```yml
containers:
  web:
    image: myapp/web
    requires:
      - fast-hipache
      - redis
      - redis
      - redis
```

the prefixes of the environment variables injected into the `web` container will be `FAST_HIPACHE`, `REDIS_1`, `REDIS_2`, and `REDIS_3`. The [docker docs](http://docs.docker.io/en/latest/use/working_with_links_names/) have more information about how the environment variables are named and injected.

- `single`: Defaults to `false`. Set to `true` if there should be a maximum of one running instance of this container per host. This option is useful for providing a host-level etcd ambassador.
- `privileged`: Defaults to `false`. Set to `true` to run the container in privileged mode by using docker's `-privileged` flag.
- `env`: A hash of environment variables to include when running the container.

```yml
env:
  API_KEY: abc123
  API_SECRET_KEY: secret123
```

- `volumes`: A hash of volumes to include when running the container. These volumes will be mounted from the host in the cluster.

```yml
volumes:
  /destination/in/container: /source/from/host
  /ssl/server.crt: /media/state/ssl/server.crt
```

- `cmd`: A command to run in the container.

- `ports`: TODO Enables semantic port names through etcd.

- `endpoints`: A list of Services or Instances that the container will have access to through etcd. If the endpoints are 'foo-service' and 'bar-instance', the container will be mounted with a global ambassador that listens to the endpoints on different ports and proxies each one on different ports, injecting the environment variable of each.
SERVICE_PROXY=127.0.0.1: don't use for now, just go off of raw etcd.


If a container has no options apart from `image`, it can be simply defined with `<name>: <image>`:

```yml
containers:
  mongo: bowery/mongo
  redis: crosbymichael/redis
```

Any container option can be overridden wherever the container is referenced. This enables flexible, declarative configuration to be used. For example, with the following config:

```yml
containers:
  app:
    requires:
      nginx:
        env:
          SERVER_CRT: /ssl/server.crt
          SERVER_KEY: /ssl/server.key
          CA_CRT: /ssl/ca.crt
        volumes:
          /media/state/keys/server.crt: /ssl/server.crt
          /media/state/keys/server.key: /ssl/server.key
          /media/state/keys/ca.crt: /ssl/ca.crt
```

#### Services
A Service is a scalable group of Service Units.

#### Scale
Services are the a.

#### Instances
Services are the a.

#### Machines


```yml

```

The config is separated into different blocks.

The image that a container uses does not have to be present on the machine compiling the service files. The image just has to be able to be pulled from anywhere in the cluster.

Usage
-----

Right now, consoled has only one option: `make`. You can use the `make` option to generate service files.

`consoled.py make -f <config_file> <output_dir>`

This will parse `config_file` and output the generated service files to `output_dir`. Existing service files will be overwritten on conflict.

```bash
$ ./consoled.py make -f config.yml services
23 service files written to ./services
```

By default, consoled reads config from stdin so you can do nice things like piping files.

```bash
$ ./consoled.py make services/production < production.yml
14 service files written to ./services/production
```

Since consoled also accepts JSON-formatted input through a file or stdin, it can be easily integrated with other tools.

Tips for good configuration
---------------------------

- Add **polvi/docker-reg** to all-hosts.

```yml
containers:
  docker-reg:
    image: polvi/docker-reg
  single: true

all-containers:
  requires:
    - docker-reg
```

Polvi's **docker-reg** will now heartbeat all container endpoints for all hosts that have containers running. If we want docker to be checked on every host regardless of whether it's running containers or not, just use:

```yml
all-hosts:
  - docker-reg
```yml



Provisioning
-------------
Since fleet doesn't have an option to run a certain services on all hosts in the cluster, we can have the service run automatically when provisioned.

Firewall Ideas
--------------
When hosts are provisioned with coreos-cloudinit, the firewall can configure iptables to block everything except the localhost interface and etcd. Consoled can have an option to wait units a container starts, inspect the container, then open the ports in the firewall. When the container closes, it will close the ports.