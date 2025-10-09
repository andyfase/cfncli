import os
import json
from cfncli.ext_customizations.cloudformation.yamlhelper import yaml_parse, yaml_dump
from collections import namedtuple

from cfncli.cli.utils.pprint import echo_pair
from .command import Command


class StackExportOptions(namedtuple("StackExportOptions", ["output_dir"])):
    pass


class StackExportCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # print stack qualified name
        self.ppt.pprint_stack_name(stack_context.stack_key, parameters["StackName"], "Exporting config for stack ")
        self.ppt.pprint_session(session)

        # Package before export
        stack_context.run_packaging()

        # create output directory if not exists
        if not os.path.exists(self.options.output_dir):
            os.mkdir(self.options.output_dir)

        stack_output_name = stack_context.stack_key.replace(".", "_")

        ## write packaged template file
        template_type = "json" if parameters.get("TemplateBody", "").startswith("{") else "yaml"
        with open(f"{self.options.output_dir}/{stack_output_name}_template.{template_type}", "w") as f:
            if template_type == "json":
                temp = json.loads(parameters.get("TemplateBody", {}))
                json.dump(temp, f, indent=4)
            else:
                temp = yaml_parse(parameters.get("TemplateBody", "{}"))
                print(yaml_dump(temp), file=f)

        ## generate parameters file
        with open(f"{self.options.output_dir}/{stack_output_name}_parameters.json", "w") as f:
            json.dump(parameters.get("Parameters", []), f, indent=4)

        ## generate tags file
        with open(f"{self.options.output_dir}/{stack_output_name}_tags.json", "w") as f:
            json.dump(parameters.get("Tags", []), f, indent=4)

        return (True, {})
