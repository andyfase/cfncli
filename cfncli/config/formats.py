# -*- coding: utf-8 -*-

import copy
import os

import jsonschema
import six
from deepmerge import conservative_merger

from .deployment import StackKey, StackDeployment, StackMetadata, StackProfile, StackParameters, Deployment
from .schema import load_schema
from .template import find_references

CANNED_STACK_POLICIES = {
    "ALLOW_ALL": '{"Statement":[{"Effect":"Allow","Action":"Update:*","Principal":"*","Resource":"*"}]}',
    "ALLOW_MODIFY": '{"Statement":[{"Effect":"Allow","Action":["Update:Modify"],"Principal":"*","Resource":"*"}]}',
    "DENY_DELETE": '{"Statement":[{"Effect":"Allow","NotAction":"Update:Delete","Principal":"*","Resource":"*"}]}',
    "DENY_ALL": '{"Statement":[{"Effect":"Deny","Action":"Update:*","Principal":"*","Resource":"*"}]}',
}


class FormatError(Exception):
    pass


def load_format(version):
    if version == 3:
        return FormatV3
    elif version == 2:
        return FormatV2
    elif version == 1 or version is None:
        return FormatV1
    else:
        raise FormatError("Unspported config version {}".format(version))


class ConfigFormat(object):
    VERSION = None

    def validate(self, config):
        raise NotImplementedError

    def parse(self, config):
        raise NotImplementedError


class FormatV1(ConfigFormat):
    VERSION = "1.0.0"

    def __init__(self, **context):
        self._context = context

    def validate(self, config):
        schema = load_schema(str(self.VERSION))
        jsonschema.validate(config, schema)

    def parse(self, config):
        raise NotImplementedError


class FormatV2(ConfigFormat):
    VERSION = "2.0.0"

    STAGE_CONFIG = dict(Order=(six.integer_types, None), Config=(dict, {}))

    STACK_CONFIG = dict(
        Order=(six.integer_types, None),
        Profile=(six.string_types, None),
        Region=(six.string_types, None),
        Package=(bool, None),
        ArtifactStore=(six.string_types, None),
        StackName=(six.string_types, None),
        Template=(six.string_types, None),
        Parameters=(dict, None),
        DisableRollback=(bool, None),
        RollbackConfiguration=(dict, None),
        TimeoutInMinutes=(six.integer_types, None),
        NotificationARNs=(six.string_types, None),
        Capabilities=(list, None),
        ResourceTypes=(list, None),
        RoleARN=(six.string_types, None),
        OnFailure=(six.string_types, None),
        StackPolicy=(six.string_types, None),
        Tags=(dict, None),
        ClientRequestToken=(six.string_types, None),
        EnableTerminationProtection=(bool, None),
    )

    def __init__(self, basedir="."):
        self._basedir = basedir

    def validate(self, config):
        schema = load_schema(str(self.VERSION))
        jsonschema.validate(config, schema)

        if have_parameter_reference_pattern(config):
            raise jsonschema.SchemaError("Do not support parameter reference in config version <= 2")

    def parse(self, config):
        deployment = Deployment()
        blueprints = config.get("Blueprints", dict())
        stages = config.get("Stages", dict())
        for stage_key, stage_stacks in stages.items():
            stacks = copy.deepcopy(stage_stacks)
            stage_config = stacks.get("Config", {})
            stage_extend_name = stage_config.get("Extends", None)
            stage_extend = stages.get(stage_extend_name, None)
            if stage_extend_name and not stage_extend:
                raise FormatError('Stage Extend "%s" not found' % stage_extend_name)
            if stage_extend:
                stage_config.pop("Extends", {})
                stage_extend_config = stage_extend.get("Config", {})
                conservative_merger.merge(stage_config, stage_extend_config)
                conservative_merger.merge(stacks, stage_extend)

            if not stage_config.get("Order", None):
                stage_config["Order"] = 999
            for stack_key, stack_config in stacks.items():
                if stack_key == "Config":
                    continue
                base = dict()
                blueprint_id = stack_config.get("Extends")
                if blueprint_id:
                    blueprint = blueprints.get(blueprint_id)
                    if not blueprint:
                        raise FormatError('Blueprint "%s" not found' % blueprint_id)
                    base = copy.deepcopy(blueprint)

                conservative_merger.merge(stack_config, base)
                stack = self._build_stack(stage_key, stack_key, stage_config, copy.deepcopy(stack_config))
                deployment.add_stack(stage_key, stack_key, stack)

        return deployment

    def _build_stack(self, stage_key, stack_key, stage_config, stack_config):
        # add default order
        stage_order = stage_config.get("Order", 0)
        stack_order = stack_config.get("Order", 0)
        stack_config["Order"] = (stage_order, stack_order)

        # add default name
        if "StackName" not in stack_config:
            stack_config["StackName"] = stack_key

        ## add prefix to stack name if set in config
        if "StackPrefix" in stage_config:
            stack_config["StackName"] = "".join([stage_config["StackPrefix"], stack_config["StackName"]])

        ## add any stage parameters to stack parameters
        if "Parameters" in stage_config:
            if not stack_config.get("Parameters", None):
                stack_config["Parameters"] = stage_config["Parameters"]
            else:
                ## allow Stack parameters to overwrite Stage Parameters
                stage_parameters = copy.deepcopy(stage_config["Parameters"])
                stage_parameters.update(stack_config["Parameters"])
                stack_config["Parameters"] = stage_parameters

        # Make relate template path
        template = stack_config.get("Template")
        if template and not (template.startswith("https") and template.startswith("http")):
            template_path = os.path.realpath(os.path.join(self._basedir, template))
            if not os.path.exists(template_path):
                raise FormatError("File Not Found %s" % template_path)
            stack_config["Template"] = template_path

        stack_policy = stack_config.get("StackPolicy")
        if stack_policy and stack_policy not in CANNED_STACK_POLICIES:
            stack_policy_path = os.path.realpath(os.path.join(self._basedir, stack_policy))
            if not os.path.exists(stack_policy_path):
                raise FormatError("File Not Found %s" % stack_policy_path)
            stack_config["StackPolicy"] = stack_policy_path

        key = StackKey(StageKey=stage_key, StackKey=stack_key)
        stack_profile = StackProfile.from_dict(**stack_config)
        stack_parameters = StackParameters.from_dict(**stack_config)
        stack_metadata = StackMetadata.from_dict(**stack_config)

        stack = StackDeployment(key, stack_metadata, stack_profile, stack_parameters, stage_config)

        return stack


def have_parameter_reference_pattern(config):
    match = find_references(config)
    return len(match) > 0


class FormatV3(FormatV2):
    VERSION = "3.0.0"

    def validate(self, config):
        schema = load_schema(str(FormatV2.VERSION))  # use same schema as v2
        jsonschema.validate(config, schema)
