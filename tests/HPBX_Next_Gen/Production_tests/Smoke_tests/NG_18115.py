# -*- coding: utf-8 -*-

from __future__ import absolute_import

from context import Context
from call_functions import PagingCall

from step_manager.pbxut import StepTestCase


class NG_18115(StepTestCase):
    """
    @name: NG_18115
    @summary: Paging call with answer
    @suite: HPBX_Next_Gen.Automation_functional_tests.Paging
    """

    def setUp(self):
        self.context = Context.instance()

        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')
        self.cf = self.context.get("client_factory")
        self.user1.acquire_sip_client(self.cf)
        self.user2.acquire_sip_client(self.cf)
        self.user3.acquire_sip_client(self.cf)

        self.pg1 = self.context.get('pg1')

    def initialize(self, sm):

        # build execute info
        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "listeners": [self.user3.get_sipre_client()],
            "call_to": self.user1.get_sip_uri(self.pg1.get_extension()),
            "default_check_audio": True,
            "convert_to_call": self.user1.get_account().get_page_to_twowaycall_action(),
            "sm": sm,
        }

        PagingCall(**execute_info)

        # check call history
        call_1 = {'from': self.user1.get_extension(), 'caller_name': self.user1.get_display_name(),
                  'to': self.pg1.get_extension(), 'called_name': self.user2.get_display_name()}
        call_2 = {'from': self.user1.get_extension(), 'caller_name': self.user1.get_display_name(),
                  'to': self.pg1.get_extension(), 'called_name': self.user3.get_display_name()}

        sm.add_step("Check call history").add_expected(self.user1.get_account().check_call_history, calls=[call_1, call_2])

    def tearDown(self):
        self.user1.release_client()
        self.user2.release_client()
        self.user3.release_client()
