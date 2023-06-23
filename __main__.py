#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import exit, argv
from logging import getLogger
from pbxut import PBXTestRunner
from pbxut.loaders.directory import DirectoryTestLoader
from pbxut_util import ContextManager
from pbxut_util.mapper import ContextReader
from context import Context

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml import load, dump
from logging.config import dictConfig


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
        name = argv[1]
        config_name = "./settings/settings.xml"
        admin_login = argv[2]
        admin_password = argv[3]

        file_context = cr.read(config_name)

        # Step 3. Create plugins
        global_context = Context.instance()
        global_context.set("unison_login", admin_login)
        global_context.set("unison_password", admin_password)
        global_context.set("production", True)
        global_context.set("server_name", name)
        for plugin in file_context.plugins:
            self.__log.debug('Create plugin: plugin_class = {plugin_class!r}'.format(plugin_class=plugin.plugin_class))
            if plugin.plugin_id == "MailReporterPlugin":
                subject = f'[AUTOTEST] {name} smoke production report:'+' {{ case_resolution }}'
                subject = ("subject", subject)
                plugin.params.append(subject)
            elif plugin.plugin_id == "ContextPlugun":
                plugin.params.append(("test_profile", name))
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
        server_name = argv[1]
        with open("./logging.yaml", "rb") as stream:
            content = stream.read()
        config = load(content, Loader=Loader)
        for handler in config["handlers"]:
            config["handlers"][handler]["filename"] = config["handlers"][handler]["filename"]+"_"+str(server_name)+".log"
        dictConfig(config)

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
