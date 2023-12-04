# -*- coding: utf-8 -*-

import sys
import logging

from .boto3_context import Boto3DeploymentContext
from .boto3_outputs import Boto3OutputStore
from .base import RunBook, RunBookError


class Boto3RunBook(RunBook):
    def __init__(self, profile, artifact_store, manager, selector, pretty_printer):
        RunBook.__init__(self)

        self._profile = profile
        self._artifact_store = artifact_store
        self._manager = manager
        self._selector = selector
        self._ppt = pretty_printer
        selected_deployments = self._manager.query_stacks(
            self._selector.stage_pattern,
            self._selector.stack_pattern)
        selected_stack_keys = list(
            d.stack_key.qualified_name for d in selected_deployments)

        if len(selected_deployments) == 0:
            self._ppt.secho('No stack matches specified pattern.', fg='red')
            self._ppt.secho('Available stacks are:')
            for s in self._manager.query_stacks():
                self._ppt.secho(' {}'.format(s.stack_key.qualified_name))
            sys.exit()

        ## If stage config sets a deployment account confirm account is valid - perform this check once per stage we are deploying too.
        ## Skip this check if the stack deployment profile is set (as this explicity defined a AWS CLI profile for the deployment)
        checked_stages = []
        for deployment in selected_deployments:
            stage_account = deployment.stage_config.get('Account', None)
            profile = deployment.profile.Profile
            if stage_account and profile is None and deployment.stack_key.StageKey not in checked_stages:
                ## confirm deployment context is set to deploy within given stage account
                context = Boto3DeploymentContext(self._profile, self._artifact_store, deployment, self._ppt)
                deployment_account = self.get_account(context)
                if stage_account != deployment_account:
                    self._ppt.secho(
                        (
                            f"Stage {deployment.stack_key.StageKey} configured for account: {stage_account} "
                            f"but profile set as account: {deployment_account}"
                        ),
                        fg='red'
                    )
                    sys.exit()
                checked_stages.append(deployment.stack_key.StageKey)
                    
        whole_deployments = self._manager.query_stacks()
        whole_contexts = []
        for deployment in whole_deployments:
            context = Boto3DeploymentContext(
                self._profile, self._artifact_store, deployment, self._ppt)
            if deployment.stack_key.qualified_name in selected_stack_keys:
                self._contexts.append(context)
            whole_contexts.append(context)

        self._output_store = Boto3OutputStore(whole_contexts, self._ppt)

    def pre_run(self, command, context):
        if not command.SKIP_UPDATE_REFERENCES:
            attributes = context.get_parameters_reference()
            self._output_store.collect_stack_outputs(*attributes)
            context.update_parameters_reference(**self._output_store.get_outputs())
        context.make_boto3_parameters()
        
    def get_account(self, context):
        return context.session.client('sts').get_caller_identity().get('Account')

        
