from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import SimpleCallVM, CheckVMCP, CheckEMail
from context import Context
import subprocess


class NG_19638(StepTestCase):
    """
    @name: NG-19638
    @summary: WebRTC call to VM
    @suite: HPBX_Next_Gen.Production_tests.Smoke_tests
    """

    def setUp(self):
        self.context = Context.instance()
        self.user5 = self.context.get("user5")
        self.user2 = self.context.get("user2")
        self.user2.disable_vm_transcript()
        self.device = self.user5.create_device(name="webrtc")
        self.user2.delete_all_voicemails()

    def initialize(self, sm):
        # build execute info
        check_vm_cp_step = CheckVMCP(
            vm_data=self.user2.get_last_voicemail,
            freqs=[139, 431],
            sender_number=self.user5.get_extension()
        )

        # run the test
        sm.add_step("Start virtual desktop and make call to User2",
                    action=subprocess.run,
                    args=f"Xvfb :1 -screen 1 1024x768x16 >/dev/null 2>&1 & export DISPLAY=:1 && intermedia-ring -- "
                    f"--realm={self.user5.account.get_cluster_addr()} --user={self.device.get_device_id()} "
                    f"--password={self.device.get_pwd()} --phoneNumber={'*'+self.user2.get_extension()} >/dev/null 2>&1",
                    shell=True, duration=5.0)

        sm.add_step("Wait for message", duration=40)

        check_vm_cp_step.add_substeps_to_step(sm.add_step("Check received VM from CP for user2"))

    def tearDown(self):
        self.user5.delete_device(alias="webrtc")
