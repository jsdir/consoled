class Container(object):

    defaults = {
        'single': False,
        'privileged': False
    }

    def __init__(self, name, options):
        self.name = name

        if isinstance(options, dict):
            self.setOptions(options)
        else:
            self.source = options

    def setOptions(self, options):
        # A Container defined with options must have a source.
        try:
            self.source = options['source']
            self.setOptions(options)
        except:
            raise KeyError('No source defined for container: %s' % name)

        # Use the defaults during assignment.
        self.is_single = options.get('single', defaults['single'])
        self.is_privileged = options.get('privileged', defaults['privileged'])

        self.cmd = options.get('cmd')
        self.env = options.get('env')

        # Endpoints can be Services or Instances.
        self.endpoint_names = options.get('endpoints')

        self.require(options.get('requires'))
        self.setEndpoints(options.get('endpoints'))

    def require(self, requires):
        # Only other Containers can be requires.
        for require in requires:
            if require == self.name:
                raise NameError('Container "%s" required itself.', self.name)
        self.require_names = requires


class Service(object):
    def __init__(self, name, options):
        # Instance defaults
        self.scale = 0

        self.name = name
        self.container_names = options


class Machine(object):
    def __init__(self, match, obj_names):
        self.match = match
        self.obj_names = obj_names


toplevel_options = [
    "every_image",
    "every_machine",
]


def checkNameConflicts(obj_maps):
    name_map = {}
    for obj_map in obj_maps:
        for key, value in obj_map:
            if key in name_map:
                raise NameError('Name "%s" already exists in config.' % key)
            name_map[key] = value


def register(key, obj, config):
    objs = {}
    for name, value in config.get(key, {}):
        objs[name] = obj(name, value)
    return objs

def parse_config(config):
    # Register Containers.
    containers = register('containers', Container, config)

    # Register Services.
    services = register('services', Service, config)

    # Apply scale to services.
    for service_name, amount in config.get('scale', {}):
        services[service_name].scale = amount

    # Register Instances.
    instances = register('instances', lambda name, _: containers[name], config)

    checkNameConflicts([containers, services, instances])
    hosts = register('hosts', Host, config)

    # Save instance unit files when finished looping through hosts.

    # 


class ServiceFile(object):
    def __init__(self, service):
        self.contents = 4

    def save_to(self, path):
        with open(os.path.join(path, self.get_file_name())) as f:
            f.write(self.get_contents())


def build(config_path, services_path):
    # The file is the environment
    config = parse_config(config_path)

    for pattern, objs in config.hosts:

    for instance in config.instances:
        instance

    for service in config.services:
        service

    config.
    config.scale = {""}
    for service, scale in config.scale:
        for i in range(scale):
            ServiceFile(service, i).save_to(services_path)


# reads scaling amount
# reads services
# generates many .service files

"""
A Service is a scalable group of containers. The containers don't have to be homogeneous
Service Unit is a homogeneous division of a Service. A service will have many identical service units.

This is useful if you want two different components running on the same machine.

Consoled will only scale services.

"""


Custom sizes can override in the api
|
V
consoled build stretch.yml services

"""
Do environments get "deployed"?

the consoled tool loads the environments into objects

consoled scale staging/* web=6
> finds the machine that web runs on and adds one to the backend
environments.yml
----------------

consoled expects and can orchestrate CoreOS machines, or any other machine that has a functional fleet and docker installation.

test:
  rackspace-salt:
    options: value


staging:
  dfw:
    backend: rackspace-salt
    backend_options:
      key: value
      everything: ha
      region: dfw

production:
  dfw:
    backend: rackspace-salt
    backend_options:
      key: value
      everything: ha
      region: dfw

  lon:
    backend: rackspace-salt
    backend_options:
      key: value
      everything: ha
      region: dfw


If you have only one backend with a type, 
local:
  vagrant: # no need for a backend label, this functions as the backend type. Only one
    key_value: 2
    v: 3

"""