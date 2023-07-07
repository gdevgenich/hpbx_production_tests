# -*- coding: utf-8 -*-

from __future__ import absolute_import

from call_functions import SimpleCall
from context import Context
from step_manager.pbxut import StepTestCase


class NG_18110(StepTestCase):
    """
    @name: NG-18110
    @summary: Simple call from PSTN
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get('external_user1')
        self.user2 = self.context.get('user1')

    def initialize(self, sm):
        # build execute info
        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "alice": self.user2.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.user2.get_phone_number()),
            "default_check_audio": True,
            "sm": sm,
            "work_dir": "/var/tmp/pjlog/",
            "wav_file": "/opt/smoke_production/audio/test_audio_139_431.wav"
        }

        # run the test
        SimpleCall(**execute_info)

    def tearDown(self):
        pass
