# -*- coding: utf-8 -*-
from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import OrderedCall
from context import Context


class NG_18116(StepTestCase):
    """
    @name: NG-18116
    @summary: Call from PSTN to a user with simultaneous FMFM to two internal users
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.external_user3 = self.context.get('external_user1')
        self.user2 = self.context.get('user1')
        self.user3 = self.context.get('user2')
        self.user4 = self.context.get('user3')
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
            "default_check_audio": False,
            "sm": sm,
            "work_dir": "/var/tmp/pjlog/",
            "wav_file": "/opt/smoke_production/audio/test_audio_139_431.wav"
        }

        # run the test
        OrderedCall(**execute_info)

    def tearDown(self):
        self.user2.remove_all_fmfm()
