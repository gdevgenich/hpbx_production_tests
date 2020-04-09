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
        self.user5 = self.context.get("user5")
        self.user2 = self.context.get("user2")
        self.device = self.user5.create_device()
        self.user2.delete_all_voicemails()

    def initialize(self, sm):
        sm.add_step("Start virtual desktop", action=subprocess.run, args="Xvfb :1 -screen 1 1024x768x16 & export "
                                                                         "DISPLAY=:1 && intermedia-ring -- "
                                                                         "--realm={server} --user={device_id} "
                                                                         "--password={pwd} --phoneNumber={extension} "
                                                                         "--ignoreCertificateErrors".format(server=self.user5.get_account().get_server(),
                                                                                                            device_id=self.device.get_device_id(),
                                                                                                            pwd=self.device.get_pwd(),
                                                                                                            extension=self.user2.get_extension()), shell=True, duration=5.0)
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
