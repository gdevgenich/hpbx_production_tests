# -*- coding: utf-8 -*-

from __future__ import absolute_import

from call_functions import SimpleCall, CheckIncomingSound, TwoWayCheckAudio, CheckCR, CheckEMail
from context import Context
from step_manager.pbxut import StepTestCase


class NG_18109(StepTestCase):
    """
    @name: NG-18109
    @summary: Simple call recorded automatically
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('external_user1')

        self.user1.enable_call_recording_always()
        self.user1.enable_cr_warning_tone()

        self.freqs = [113, 391]
        self.gcrb_freqs = self.context.get('gcrb_freqs')

    def initialize(self, sm):
        # build execute info
        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.user2.get_phone_number()),
            "default_check_audio": False,
            "sm": sm,
            "work_dir": "/var/tmp/pjlog/",
            "wav_file": "/opt/smoke_production/audio/test_audio_139_431.wav"
        }

        check_call_audio = TwoWayCheckAudio(self.user1.get_sipre_client(), self.user2.get_sipre_client(),
                                            custom_freqs=self.freqs, work_dir="/var/tmp/pjlog/",
                                            wav_file="/opt/smoke_production/audio/test_audio_113_391.wav")

        check_cr = CheckCR(cr_data=self.user1.get_last_call_recording_info,
                           cr_file=self.user1.download_last_call_recording, recipient=None,
                           freqs=self.freqs, duration=24, duration_range=3, path="/var/tmp/pjlog/")

        # run the test
        SimpleCall(**execute_info)

        sm.find_step("Check devices are connected").add_substep("Skip GCRB cheking", duration=10)

        check_call_audio.add_substeps_to_step(sm.find_step("Check devices are connected"))

        sm.add_step("Wait for recording", duration=5.0)

        check_cr.add_substeps_to_step(sm.add_step("Check CR"))

    def tearDown(self):
        self.user1.disable_call_recording()
