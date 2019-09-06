#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import exit, argv
from logging import getLogger

from log_functions import prepare_logging_system

from pbxut import PBXTestRunner
from pbxut.loaders.directory import DirectoryTestLoader

from pbxut_util import ContextManager
from pbxut_util.mapper import ContextReader
from context import Context


class TestProgram(object):
    """ Test program new
    """

    def __init__(self):
        self.__log = getLogger('app')


    def dispose(self):
        """ Dispose
        """

    def pre_process(self, runner):
        """ Pre-process hook
        """
        # Step 1. Create new context manager (create new instance)
        cm = ContextManager()

        # Step 2. Reading parameters
        cr = ContextReader()
        config_name = "./settings/settings_hpbx2.xml"
        name = argv[1]
        admin_login = argv[2]
        admin_password = argv[3]

        file_context = cr.read(config_name)

        # Step 3. Create plugins
        global_context = Context.instance()
        global_context.set("unison_login", admin_login)
        global_context.set("unison_password", admin_password)
        global_context.set("production", True)
        for plugin in file_context.plugins:
            self.__log.debug('Create plugin: plugin_class = {plugin_class!r}'.format(plugin_class=plugin.plugin_class))
            inst = cm.inst_create(inst_name=plugin.plugin_class, args=[], kwargs={"context": file_context})
            cm.inst_initialize(inst, args=[runner], kwargs=plugin.params)
            runner.plugins.append(inst)
        global_context.set("production", True)

    def post_process(self, runner):
        """ Post process
        """
        while runner.plugins:
            plugin = runner.plugins.pop(0)
            plugin.dispose()


    def run(self):
        """ Run application
        """

        # Step 1. Prepare logging system
        prepare_logging_system(name="./resources/logging.yaml")

        # Create test runner (test run iterator)
        runner = PBXTestRunner(loader=DirectoryTestLoader(), failfast=False)
        #
        self.pre_process(runner)
        result = runner.run()
        self.post_process(runner)
        # P
        conditions = [
            result.is_passed(),
            not result.is_failed(),
            not result.is_error(),
        ]
        code = 0 if all(conditions) else 1  # Error: 0 - pass, 1 - test failed or error
        return code


def main():
    rc = 2  # Error: 2 - system exception
    app = TestProgram()
    try:
        rc = app.run()
    finally:
        app.dispose()
    #
    return rc


if __name__ == "__main__":
    exit(main())
