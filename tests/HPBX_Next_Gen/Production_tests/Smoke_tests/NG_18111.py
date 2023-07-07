# -*- coding: utf-8 -*-

from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from context import Context

from call_functions import BaseParkLeft, TwoWayCheckAudio
from call_functions.matchers.matchers import devices_on_call, no_active_calls_remain, check_blf_state


class NG_18111(StepTestCase):
    """
    @name: NG-18111
    @summary: Call parked from left leg unparked by other internal user
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')
        self.blf_line3 = self.context.get('blf_line3')

    def initialize(self, sm):
        # build execute info
        park_dtmf = self.user1.account.get_park_dtmf()
        park_location = self.user1.account.get_park_location_start()
        unpark_uri = self.user3.get_sip_uri(park_location)

        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.user2.get_extension()),
            "park_action": park_dtmf,
            "wav_file": "/opt/smoke_production/audio/test_audio_139_431.wav",
            "sm": sm
        }
        
        check_audio_after_unpark = TwoWayCheckAudio(self.user2.get_sipre_client(), self.user3.get_sipre_client(),
                                                    work_dir="/var/tmp/pjlog/",
                                                    wav_file="/opt/smoke_production/audio/test_audio_139_431.wav")
        
        # run the test
        BaseParkLeft(**execute_info)

        sm.add_step_after("Checking registration", "Check BLF state before test")\
            .add_expected(check_blf_state, blf_line=self.blf_line3, state="terminated")
        
        sm.add_step("Wait", None, 5.0)
        
        sm.add_step("Check BLF state before unpark")\
            .add_expected(check_blf_state, blf_line=self.blf_line3, state="terminated")
        
        sm.add_step("Unpark by user", self.user3.get_sipre_client().make_call, 2.0, dst_uri=unpark_uri)
        
        sm.add_step("Check BLF state after unpark")\
            .add_expected(check_blf_state, blf_line=self.blf_line3, state="confirmed")
                
        sm.add_step("Check devices are connected after unpark")\
            .add_expected(devices_on_call, device1=self.user2.get_sipre_client(), device2=self.user3.get_sipre_client())
        
        check_audio_after_unpark.add_substeps_to_step(sm.add_step("Check audio after unpark"))
        
        sm.add_step("End all calls", self.user2.get_sipre_client().hangup, 5.0)
        
        sm.add_step("Check BLF state after test")\
            .add_expected(check_blf_state, blf_line=self.blf_line3, state="terminated")
        
        sm.add_step("Check no active calls left")\
            .add_expected(no_active_calls_remain, devices=[self.user1.get_sipre_client(), self.user2.get_sipre_client(),
                                                           self.user3.get_sipre_client()])

    def tearDown(self):
        pass
