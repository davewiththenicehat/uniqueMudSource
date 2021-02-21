from evennia.accounts.tests import *


class TestDefaultAccountEv(TestDefaultAccountEv):
    def test_puppet_success(self):
        self.account.msg = MagicMock()
        with patch("evennia.accounts.accounts._MULTISESSION_MODE", 2):
            self.account.puppet_object(self.session, self.char1)
            self.account.puppet_object(self.session, self.char1)
            self.account.msg.assert_called_with("You are already puppeting this object.")
