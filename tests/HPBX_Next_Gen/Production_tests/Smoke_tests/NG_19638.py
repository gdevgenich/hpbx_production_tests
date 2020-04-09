from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import SimpleCallVM, CheckVMCP, CheckEMail
from context import Context
import subprocess


class NG_19638(StepTestCase):
    """
    @name: NG-19638
    @summary: WebRTC call to VM
    @suite: HPBX_Next_Gen.Automation_functional_tests
    """


    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get("user1")
        self.user2 = self.context.get("user2")
        self.user1.delete_all_voicemails()

    def initialize(self, sm):
        sm.add_step("Start virtual desktop", action = subprocess.run, args="Xvfb :1 -screen 1 1024x768x16 &", shell=True, duration=5.0)
        sm.add_step("Leave voicemail", action = subprocess.run, args="intermedia-ring -- --realm=64.78.52.88 --user=70756563 --password=123 --phoneNumber=100 --ignoreCertificateErrors", shell=True)
        sm.add_step("Wait for message", duration=40)

        # getting transcript from third-party service takes long time
        # here we assume that if email is sent, then file is present on FS

        check_vm_cp_step = CheckVMCP(
            vm_data=self.user2.get_last_voicemail,
            vm_transcript=self.user2.download_last_transcript,
            sender_number=self.user1.get_extension()
        )
        check_vm_cp_step.add_substeps_to_step(
            sm.add_step("Check received VM from CP for user2")
        )

    def tearDown(self):
        pass
