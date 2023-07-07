# -*- coding: utf-8 -*-

from __future__ import absolute_import

from context import Context
from step_manager.pbxut import StepTestCase

from call_functions import SimpleCallDTMF


class NG_18097(StepTestCase):
    """
    @name: NG-18097
    @summary: Pick up a call after AA transfer
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')
        self.aa1 = self.context.get('aa1')

    def initialize(self, sm):
        # build execute info
        pickup_string = f"{self.user1.account.get_direct_pickup_prefix()}{self.user3.get_extension()}"

        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.aa1.get_extension()),
            "dtmf": [("5", 2.0), ("5", 2.0), ("5", 2.0)],
            "sm": sm,
            "work_dir": "/var/tmp/pjlog/",
            "wav_file": "/opt/smoke_production/audio/test_audio_139_431.wav"
        }

        # run the test
        SimpleCallDTMF(**execute_info)

        sm.remove_step("Alice answer")
        sm.remove_step("Wait Alice ringing")

        sm.add_step_after("Send DTMF 5", "Alice pickup call", self.user2.get_sipre_client().make_call, duration=5.0,
                          dst_uri=self.user1.get_sip_uri(pickup_string))

        sm.add_step("Wait", duration=5.0)

        # check call history
        call_1 = {'from': self.user1.get_extension(), 'caller_name': self.user1.get_display_name(),
                  'to': self.user2.get_extension(), 'called_name': self.user2.get_display_name()}
        call_2 = {'from': self.user1.get_extension(), 'caller_name': self.user1.get_display_name(),
                  'to': self.aa1.get_extension(), 'called_name': self.aa1.get_display_name()}

        sm.add_step("Check call history")\
            .add_expected(self.user1.account.check_call_history, calls=[call_1, call_2])

    def tearDown(self):
        pass
