from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import SimpleCallVM, CheckVMCP, CheckEMail
from context import Context


class NG_18102(StepTestCase):
    """
    @name: NG-18102
    @summary: Leave message for VMG by extension
    @suite: HPBX_Next_Gen.Automation_functional_tests.VM_group
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get("user1")
        self.user2 = self.context.get("user2")
        self.user3 = self.context.get("user3")
        self.cf = self.context.get("client_factory")
        self.vmg1 = self.context.get("vmg1")
        # remove all voicemails
        self.user2.delete_all_voicemails()
        self.user3.delete_all_voicemails()
        # remove emails
        # prepare VM group
        self.vmg1 = self.context.get("vmg1")
        self.vmg1.reset()
        self.vmg1.add_member_to_vmg(self.user2)
        self.vmg1.add_member_to_vmg(self.user3)

        # transcript parameters
        self.user2.enable_vm_transcript()
        self.user3.enable_vm_transcript()
        self.vm_audio = self.context.get("vm_audio_path1")
        self.transcript = self.context.get("vm_transcript1")
        self.duration = 12

    def initialize(self, sm):

        execute_info = {
            "bob": self.user1.get_sipre_client(),
            "call_to": self.user1.get_sip_uri(self.vmg1.extension),
            "user_timeout": 2,
            "wav_file": self.vm_audio,
            "message_duration": self.duration,
            "sm": sm,
        }

        SimpleCallVM(**execute_info)

        sm.add_step("Wait for message", duration=40)

        # getting transcript from third-party service takes long time
        # here we assume that if email is sent, then file is present on FS

        check_vm_cp_step = CheckVMCP(
            vm_data=self.user2.get_last_voicemail,
            vm_transcript=self.user3.download_last_transcript,
            exp_transcript=self.transcript,
            sender_number=self.user1.get_extension()
        )
        check_vm_cp_step.add_substeps_to_step(
            sm.add_step("Check received VM from CP for user2")
        )

        check_vm_cp_step = CheckVMCP(
            vm_data=self.user3.get_last_voicemail,
            vm_transcript=self.user3.download_last_transcript,
            exp_transcript=self.transcript,
            sender_number=self.user1.get_extension()
        )
        check_vm_cp_step.add_substeps_to_step(
            sm.add_step("Check received VM from CP for user3")
        )

        call_1 = {
            'from': self.user1.get_extension(),
            'caller_name': self.user1.get_display_name(),
            'to': self.vmg1.extension,
            'called_name': self.vmg1.display_name
        }

        sm.add_step("Check call history").add_expected(
            self.user2.account.check_call_history, calls=[call_1]
        )

    def tearDown(self):
        pass
