# -*- coding: utf-8 -*-

from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import SimpleCall
from call_functions.matchers.matchers import check_blf_state
from context import Context


class NG_18096(StepTestCase):
    """
    @name: NG-18096
    @summary: Call from internal user by extension
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.blf_line2 = self.context.get('blf_line2')

    def initialize(self, sm):
        # build execute info
        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.user2.get_extension()),
            "default_check_audio": False,
            "sm": sm,
            "work_dir": "/var/tmp/pjlog/",
            "wav_file": "/opt/smoke_production/audio/test_audio_139_431.wav"
        }

        # run the test
        SimpleCall(**execute_info)

        sm.add_step_after("Checking registration", "Check BLF state before test") \
            .add_expected(check_blf_state, blf_line=self.blf_line2, state="terminated")

        sm.add_step_after("Bob make first call", "Check BLF state before answer") \
            .add_expected(check_blf_state, blf_line=self.blf_line2, state="early")

        sm.add_step_after("Check devices are connected", "Check BLF state after answer") \
            .add_expected(check_blf_state, blf_line=self.blf_line2, state="confirmed")

        sm.add_step_after("Check no active calls left", "Check BLF state after call") \
            .add_expected(check_blf_state, blf_line=self.blf_line2, state="terminated")

    def tearDown(self):
        pass
