# -*- coding: utf-8 -*-

from __future__ import absolute_import

from call_functions import SimpleCall, CheckIncomingSound, TwoWayCheckAudio, CheckCR, CheckEMail
from context import Context
from step_manager.pbxut import StepTestCase


class NG_18110(StepTestCase):
    """
    @name: NG-18110
    @summary: Simple call from external user
    @suite: HPBX_Next_Gen.Automation_functional_tests.Call_recording.Core
    """

    def setUp(self):
        self.context = Context.instance()

        self.user1 = self.context.get('external_user1')
        self.user2 = self.context.get('user1')
        self.cf = self.context.get("client_factory")
        self.user1.acquire_sip_client(self.cf)
        self.user2.acquire_sip_client(self.cf)

    def initialize(self, sm):
        # build execute info
        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.user2.get_phone_number()),
            "default_check_audio": True,
            "sm": sm
        }
        SimpleCall(**execute_info)

    def tearDown(self):
        self.user1.release_client()
        self.user2.release_client()
