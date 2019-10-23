# -*- coding: utf-8 -*-

from __future__ import absolute_import

from context import Context
from step_manager.pbxut import StepTestCase

from call_functions import SimpleCallDTMF


class NG_18097(StepTestCase):
    """
    @name: NG-18097
    @summary: Pick up a call after AA transfer
    @suite: HPBX_Next_Gen.Automation_functional_tests.Call_pick_up.Pick_up_internal_call
    @author: rsazanov
    @version: 1
    """

    def setUp(self):
        self.context = Context.instance()
        #
        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')
        self.cf = self.context.get("client_factory")
        self.user1.acquire_sip_client(self.cf)
        self.user2.acquire_sip_client(self.cf)
        self.user3.acquire_sip_client(self.cf)
        #
        self.aa1 = self.context.get('aa1')

    def initialize(self, sm):
        # build execute info
        pickup_string = self.user1.get_account().get_direct_pickup_prefix() + self.user3.get_extension()

        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.aa1.get_extension()),
            "dtmf": '5',
            "sm":sm
        }

        # run the test
        SimpleCallDTMF(**execute_info)

        sm.remove_step("Alice answer")
        sm.remove_step("Wait Alice ringing")
        sm.add_step_after("Send DTMF 5", "Alice pickup call", self.user2.get_sipre_client().make_call, 2.0,
                          dst_uri=str(self.user1.get_sip_uri(pickup_string)))

        # check call history
        call_1 = {'from': self.user1.get_extension(), 'caller_name': self.user1.get_display_name(),
                  'to': self.user2.get_extension(), 'called_name': self.user2.get_display_name()}

        sm.add_step("Check call history")\
            .add_expected(self.user1.get_account().check_call_history, calls=[call_1])

    def tearDown(self):
        self.user1.release_client()
        self.user2.release_client()
        self.user3.release_client()
