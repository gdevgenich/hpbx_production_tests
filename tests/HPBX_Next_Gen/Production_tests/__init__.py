from __future__ import absolute_import

from sys import stdout
from os import makedirs
from os.path import exists

from pbxut.framework import PBXTestSuite
from context import Context
from configparser2.yaml import loads
from sipde_client import ClientFactory
from sipne import BLFClientFactory
from step_manager import StepManager
from call_functions import SimpleCall
from hpbx_dm import AccountLoader
from mailbox_functions import MailboxMailCatcherClient, MailboxManager


class Automation_functional_tests(PBXTestSuite):
    """
    @suite: HPBX_Next_Gen.Automation_functional_tests
    """

    def setUpSuite(self):
        """ Setup data for the suite: stack, users and mapper
        """

        # Step 1. Setup common objects
        self.setup_common()

        # Step 2. Loading profile
        # read profiles
        with open("./production/resources/hpbx_profile.yaml") as stream:
                content = stream.read()
        res = loads(content)
        #
        profile = self.context.get('test_profile')
        stdout.write('Using profile: {profile!r}\n'.format(profile=profile))
        if not profile:
            raise EnvironmentError('No setup "test_profile" variable')
        # get parameters
        accounts = res.get(name="accounts", section=profile)
        main_acc = res.get(name="main_acc", section=profile)
        external_acc = res.get(name="external_acc", section=profile)

        self.ng = res.get(name="ng", section=profile)
        self.context.set("ng", self.ng)

        # step 3. Load accounts
        acc_l = AccountLoader()
        accs = acc_l.loads(accounts)
        #
        self.main_account = accs[main_acc]
        self.external_account = accs[external_acc]

        # Setup accounts
        self.setup_with_unison_cp()
        #
        self.fill_test_data_in_context()

    def tearDownSuite(self):
        """ Dispose all used handlers
        """
        self.client_factory.dispose()
        self.blf_client_factory.dispose()

        self.main_account.release_user(self.user1)
        self.main_account.release_user(self.user2)
        self.main_account.release_user(self.user3)
        self.main_account.release_user(self.user4)
        self.main_account.release_user(self.user5)
        self.main_account.release_user(self.user6)

        self.main_account.release_user(self.ccuser1)
        self.main_account.release_user(self.ccuser2)
        self.main_account.release_user(self.ccuser3)
        self.main_account.release_user(self.ccuser4)

        self.main_account.release_user(self.resource)
        self.main_account.release_user(self.faxowner)
        self.main_account.release_user(self.confbridge)

        self.external_account.release_user(self.external_user1)
        self.external_account.release_user(self.external_user2)
        self.external_account.release_user(self.external_user3)
        #
        # dispose accounts
        self.main_account.dispose()
        self.external_account.dispose()

    def setup_common(self):
        # Get context
        self.context = Context.instance()
        # Get log level
        self.debug = True if self.context.get('is_debug') == 'Yes' else False
        #
        # Create sipde factory
        # self.client_factory = ClientFactory(debug=self.debug)
        self.client_factory = ClientFactory()
        # self.client_factory.reset()
        self.context.set("client_factory", self.client_factory)
        # Create sipne factory
        self.blf_client_factory = BLFClientFactory(debug=self.debug)
        self.context.set("blf_client_factory", self.blf_client_factory)

        # create folder for audio
        audio_dir = './audio'
        if not exists(audio_dir):
            makedirs(audio_dir)

    def setup_with_unison_cp(self):
        unison_login = self.context.get("unison_login", default_value=None)
        unison_password = self.context.get("unison_password", default_value=None)
        self.main_account.initialize(unison_login=unison_login, unison_password=unison_password)
        self.main_account.create_in_account(
            number_of_users=6, number_of_ccusers=6,
            number_of_aas=2,
            number_of_hgs=3, number_of_ccs=2)

        self.main_account.create_new_pickup_group()
        self.main_account.create_new_pickup_group()

        self.main_account.create_new_paging_group()

        self.main_account.create_new_vm_group()

        self.main_account.create_new_resource()
        self.main_account.create_new_faxowner()
        self.main_account.create_new_confbridge()

        self.external_account.initialize()

    def fill_test_data_in_context(self):
        """ (describe me)
        """
        self.user1 = self.main_account.acquire_user()
        self.user2 = self.main_account.acquire_user()
        self.user3 = self.main_account.acquire_user()
        self.user4 = self.main_account.acquire_user()
        self.user5 = self.main_account.acquire_user()
        self.user6 = self.main_account.acquire_user()

        self.ccuser1 = self.main_account.acquire_ccuser()
        self.ccuser2 = self.main_account.acquire_ccuser()
        self.ccuser3 = self.main_account.acquire_ccuser()
        self.ccuser4 = self.main_account.acquire_ccuser()
        self.ccuser5 = self.main_account.acquire_ccuser()
        self.ccuser6 = self.main_account.acquire_ccuser()

        self.resource = self.main_account.acquire_resource()
        self.faxowner = self.main_account.acquire_faxowner()
        self.confbridge = self.main_account.acquire_confbridge()

        self.external_user1 = self.external_account.acquire_user()
        self.external_user2 = self.external_account.acquire_user()
        self.external_user3 = self.external_account.acquire_user()

        self.hg1 = self.main_account.acquire_hg()
        self.hg2 = self.main_account.acquire_hg()
        self.hg3 = self.main_account.acquire_hg()

        self.cc1 = self.main_account.acquire_cc()
        self.cc2 = self.main_account.acquire_cc()

        self.aa1 = self.main_account.acquire_aa()
        self.aa2 = self.main_account.acquire_aa()

        self.pupg1 = self.main_account.acquire_pupg()
        self.pupg2 = self.main_account.acquire_pupg()

        self.pg1 = self.main_account.acquire_pg()

        self.vmg1 = self.main_account.acquire_vmg()

        self.context.set("user1", self.user1)
        self.context.set("user2", self.user2)
        self.context.set("user3", self.user3)
        self.context.set("user4", self.user4)

        self.context.set("ccuser1", self.ccuser1)
        self.context.set("ccuser2", self.ccuser2)
        self.context.set("ccuser3", self.ccuser3)
        self.context.set("ccuser4", self.ccuser4)
        self.context.set("ccuser5", self.ccuser5)
        self.context.set("ccuser6", self.ccuser6)

        self.context.set("user5", self.user5)
        self.context.set("offline_user1", self.user6)
        self.context.set("resource", self.resource)
        self.context.set("faxowner", self.faxowner)
        self.context.set("confbridge", self.confbridge)

        self.context.set("external_user1", self.external_user1)
        self.context.set("external_user2", self.external_user2)
        self.context.set("external_user3", self.external_user3)

        # HGs
        self.context.set("hg1", self.hg1)
        self.context.set("hg2", self.hg2)
        self.context.set("hg3", self.hg3)

        # CCs
        self.context.set("cc1", self.cc1)
        self.context.set("cc2", self.cc2)

        # AAs
        self.context.set("aa1", self.aa1)
        self.context.set("aa2", self.aa2)

        # PickUp groups
        self.context.set("pupg1", self.pupg1)
        self.context.set("pupg2", self.pupg2)

        # Paging groups
        self.context.set("pg1", self.pg1)

        # Voicemail groups
        self.context.set("vmg1", self.vmg1)

        # Test data
        with open("./resources/vm_transcript.txt") as f:
            transcript = f.read()
        self.context.set("vm_transcript1", transcript)
        self.context.set("vm_audio_path1", "./resources/vm_audio.wav")

        if self.ng:
            stdout.write("External users CNAM:\n")
            self.get_cnam(self.external_user1, self.user1)
            self.get_cnam(self.external_user2, self.user1)
            self.get_cnam(self.external_user3, self.user1)

    def get_cnam(self, external_user, local_user):
        """
        Place a call from PSTN to see what CNAM it has
        :param external_user: PSTN user
        :param local_user: local user in organisation with a phone number assigned
        """
        local_user.assign_phone_number()
        local_user.acquire_sip_client(self.client_factory)
        external_user.acquire_sip_client(self.client_factory)

        sm = StepManager()
        execute_info = {
            "bob": external_user.get_sipre_client(),
            "alice": local_user.get_sipre_client(),
            "call_to": external_user.get_sip_uri(local_user.get_phone_number()),
            "default_check_audio": False,
            "sm": sm
        }
        SimpleCall(**execute_info)
        sm.add_substep(
            "Check devices are connected", "Store caller CNAM",
            action=sm.set, key="CNAM", value=local_user.get_sipre_client().get_remote_uri)
        sm.run()

        cnam = sm.get("CNAM")[sm.get("CNAM").find('"') + 1: sm.get("CNAM").rfind('"')]
        stdout.write("{cnam}\n".format(cnam=cnam))
        external_user.set_cnam(cnam)

        external_user.release_client()
        local_user.release_client()
        local_user.get_account().unassign_all_phone_numbers()
