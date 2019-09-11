from __future__ import absolute_import

from step_manager.pbxut import StepTestCase
from call_functions import OrderedCall
from call_functions.matchers.matchers import smart_compare
from context import Context
from hpbx_dm import combine_names


class NG_18104(StepTestCase):
    """
    @rerun: 1
    @name: NG-18104
    @summary: Ring All. All agents logged in
    @suite: HPBX_Next_Gen.Automation_functional_tests.HG.call_from_internal_user
    """

    def setUp(self):
        self.context = Context.instance()
        self.user1 = self.context.get('user1')
        self.user2 = self.context.get('user2')
        self.user3 = self.context.get('user3')
        self.user4 = self.context.get('user4')

        # prepare hunt group
        self.hg1 = self.context.get('hg1')
        self.hg1.restore_default_values()
        self.hg1.set_calling_method_for_hg('A')
        self.hg1.add_member_to_hg(self.user1)
        self.hg1.add_member_to_hg(self.user2)
        self.hg1.add_member_to_hg(self.user3)
        for member in self.hg1.get_members():
            member.change_state_of_member_in_hg()

        # prepare lists for call scenario
        self.hg_members = [
            self.user1.get_sipre_client(), self.user2.get_sipre_client(), self.user3.get_sipre_client()
            ]
        self.order = [[0, 1, 2], [0, 1, 2]]
        
        timeout = min(self.user1.get_timeout(), self.user2.get_timeout(), self.user3.get_timeout())
        tf = 5
        self.timeouts = [timeout + tf, timeout + tf, 8]

        self.history_counter = self.hg1.get_hg_call_history_count()
    
    def get_history_counter_diff(self):
        return self.hg1.get_hg_call_history_count() - self.history_counter
    
    def initialize(self, sm):

        execute_info = {
            "bob": self.user4.get_sipre_client(),
            "alice": self.user1.get_sipre_client(),
            "call_to": self.user4.get_sip_uri(self.hg1.get_extension()),
            "devices": self.hg_members,
            "order": self.order,
            "timeouts": self.timeouts,
            "sm": sm
        }

        OrderedCall(**execute_info)

        sm.add_step("Check HG history counter after test").add_expected(
            smart_compare, exp=1, real=self.get_history_counter_diff)
        
        call_1 = {
            'from': self.user4.get_extension(), 'caller_name': self.user4.get_display_name(),
            'to': self.hg1.get_extension(), 'called_name': self.hg1.get_prefixed_display_name()
        }
        call_2 = {
            'from': self.user4.get_extension(),
            'caller_name': combine_names(self.user4.get_display_name(), self.hg1.get_display_name()),
            'to': self.user1.get_extension(), 'called_name': self.user1.get_display_name()
        }

        sm.add_step("Check call history").add_expected(
            self.hg1.get_account().check_call_history, calls=[call_1, call_2])
        
        participants = {
            "number_from": self.user4.get_extension(), "from_display_name": self.user4.get_display_name(),
            "hg_name": self.hg1.get_display_name(), "hgm_name": self.user1.get_full_name()
        }
        
        sm.add_step("Get HG call history", sm.set, key="hgch", value=self.hg1.get_last_hg_call_history_call)
        sm.add_step("Check template answer member").add_expected(
            sm.call_method_of_stored_value, key="hgch", method_name="check_template_answer_member")
        sm.add_step("Check participants").add_expected(
            sm.call_method_of_stored_value, key="hgch", method_name="check_participants", **participants)
        sm.add_step("Check answered immediately").add_expected(
            sm.call_method_of_stored_value, key="hgch", method_name="check_conn_immed", should_return=False)

    def tearDown(self):
        pass
