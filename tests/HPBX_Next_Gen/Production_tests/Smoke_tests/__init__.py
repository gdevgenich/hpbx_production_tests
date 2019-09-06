# -*- coding: utf-8 -*-

from __future__ import absolute_import

from time import sleep

from pbxut.framework import PBXTestSuite
from context import Context


class check_callee(PBXTestSuite):
    """
    @suite: HPBX_Next_Gen.Automation_functional_tests.BLF.check_callee
    """

    def setUpSuite(self):
        # Get context
        self.context = Context.instance()

        self.cf = self.context.get('client_factory')
        self.bf = self.context.get('blf_client_factory')

        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')

        self.user1.cleanup()
        self.user2.cleanup()
        self.user3.cleanup()

        self.external_user1 = self.context.get('external_user1')

        # prepare phone numbers
        self.user1.get_account().unassign_all_phone_numbers()
        #
        self.user1.assign_phone_number()
        self.user2.assign_phone_number()
        self.user3.assign_phone_number()

        self.user1.acquire_sip_client(self.cf)
        self.user2.acquire_sip_client(self.cf)
        self.user3.acquire_sip_client(self.cf)
        self.external_user1.acquire_sip_client(self.cf)

        self.blf = self.user3.acquire_blf_client(self.bf)
        sleep(2)
        self.blf_line2 = self.blf.getAC().createLine(name=self.user2.get_extension(),
                                                     uri=self.user2.get_sip_uri(self.user2.get_extension()),
                                                      interval=3500, expire=3600)
        self.context.set('blf_line2', self.blf_line2)
        sleep(3)

        self.aa1 = self.context.get('aa1')
        self.aa1.bh.remove_all_actions()
        self.aa1.bh.create_action(action='ext', dtmf='5', destination=self.user3.get_extension())

    def tearDownSuite(self):
        self.user1.get_account().unassign_all_phone_numbers()

        self.user1.release_client()
        self.user2.release_client()
        self.user3.release_client()
        self.external_user1.release_client()
        self.blf_line2.remove()
