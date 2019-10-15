# -*- coding: utf-8 -*-
from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import OrderedCall
from call_functions.matchers.matchers import smart_compare
from context import Context


class NG_18116(StepTestCase):
    """
    @name: NG-18116
    @summary: FMFM_sim_two_internal_users_ext_ext
    @suite: HPBX_Next_Gen.Automation_functional_tests.FMFM_sim.call_from_external_user
    @version: 1
    """

    def setUp(self):
        self.context = Context.instance()
        self.external_user3 = self.context.get('external_user1')
        self.user2 = self.context.get('user1')
        self.user3 = self.context.get('user2')
        self.user4 = self.context.get('user3')
        self.cf = self.context.get("client_factory")
        self.user2.acquire_sip_client(self.cf)
        self.user3.acquire_sip_client(self.cf)
        self.user4.acquire_sip_client(self.cf)
        self.external_user3.acquire_sip_client(self.cf)
        self.user2.remove_all_fmfm()
        self.user2.add_fmfm(number=self.user3.get_extension(), order=50, timeout=10)
        self.user2.add_fmfm(number=self.user4.get_extension(), order=50, timeout=10)

        self.devices = [
            self.user2.get_sipre_client(), self.user3.get_sipre_client(),
            self.user4.get_sipre_client()]

        self.order = [[0], [1, 2]]

        self.timeouts = [20, 6, 2]

    def initialize(self, sm):
        # build execute info

        execute_info = {
            "bob": self.external_user3.get_sipre_client(),
            "alice": self.user4.get_sipre_client(),
            "call_to": self.external_user3.get_sip_uri(self.user2.get_phone_number()),
            "devices": self.devices,
            "order": self.order,
            "timeouts": self.timeouts,
            "sm": sm
        }

        OrderedCall(**execute_info)

        # check call history
        call_1 = {'from': self.external_user3.get_phone_number(), 'caller_name': self.external_user3.get_cnam(),
                  'to': self.user2.get_phone_number(), 'called_name': self.user2.get_display_name()}

        #sm.add_step("Check call history").add_expected(
        #     self.user2.get_account().check_call_history, calls=[call_1])

    def tearDown(self):
        self.user2.remove_all_fmfm()
        self.user2.release_client()
        self.user3.release_client()
        self.user4.release_client()
        self.external_user3.release_client()
