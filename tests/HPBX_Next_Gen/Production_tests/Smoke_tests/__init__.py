# -*- coding: utf-8 -*-

from __future__ import absolute_import

from time import sleep

from pbxut.framework import PBXTestSuite
from context import Context
from audio_functions import AudioFileGenerator
from hpbx_dm._MediaManager import MediaManager


class check_callee(PBXTestSuite):
    """
    @suite: HPBX_Next_Gen.Automation_functional_tests.BLF.check_callee
    """

    def setUpSuite(self):
        # Get context
        self.context = Context.instance()

        self.cf = self.context.get('client_factory')
        self.bf = self.context.get('blf_client_factory')

        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')
        self.user4 = self.context.get('user4')

        self.user1.cleanup()
        self.user2.cleanup()
        self.user3.cleanup()
        self.user4.cleanup()

        self.external_user1 = self.context.get('external_user1')

        # prepare phone numbers
        self.user1.get_account().unassign_all_phone_numbers()
        #
        self.user1.assign_phone_number()

        self.user1.acquire_sip_client(self.cf, path="/var/tmp/pjlog")
        self.user2.acquire_sip_client(self.cf, path="/var/tmp/pjlog")
        self.user3.acquire_sip_client(self.cf, path="/var/tmp/pjlog")
        self.external_user1.acquire_sip_client(self.cf, path="/var/tmp/pjlog")

        self.user1.change_timeout(20)
        self.user2.change_timeout(20)
        self.user3.change_timeout(20)

        self.blf = self.user4.acquire_blf_client(self.bf)
        sleep(2)
        self.blf_line2 = self.blf.getAC().createLine(name=self.user2.get_extension(),
                                                     uri=self.user2.get_sip_uri(self.user2.get_extension()),
                                                      interval=3500, expire=3600)
        self.context.set('blf_line2', self.blf_line2)
        sleep(3)
        self.blf_line3 = self.blf.getAC().createLine(name=self.user3.get_extension(),
                                                     uri=self.user3.get_sip_uri(self.user3.get_extension()),
                                                     interval=3500, expire=3600)
        self.context.set('blf_line3', self.blf_line3)
        sleep(3)

        self.aa1 = self.context.get('aa1')
        self.aa1.bh.remove_all_actions()
        self.aa1.bh.create_action(action='ext', dtmf='5', destination=self.user3.get_extension())

        self.user1.get_account().enable_call_recording()
        gcrb_freqs = [197, 313]
        gcre_freqs = [127, 617]
        self.context.set('gcrb_freqs', gcrb_freqs)
        self.context.set('gcre_freqs', gcre_freqs)

        gcrb_file = "/opt/smoke_production/audio/test_audio_197_313.wav"
        gcre_file = "/opt/smoke_production/audio/test_audio_127_617.wav"

        mm = MediaManager(account=self.user1.get_account())
        mm.deactivate_gcrb()
        mm.deactivate_gcre()
        mm.upload(name='gcrb_197_313', purpose='GCRB', path=gcrb_file)
        mm.upload(name='gcre_127_617', purpose='GCRE', path=gcre_file)

        self.pg1 = self.context.get('pg1')
        self.pg1.add_member_to_pg(self.user2)
        self.pg1.add_member_to_pg(self.user3)

    def tearDownSuite(self):
        self.user1.get_account().unassign_all_phone_numbers()
        self.user1.get_account().disable_call_recording()

        self.user1.release_client()
        self.user2.release_client()
        self.user3.release_client()
        self.external_user1.release_client()
        self.blf_line2.remove()
        self.blf_line3.remove()
