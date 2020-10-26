from evennia.commands.default.tests import CommandTest
from typeclasses.characters import Character
from commands import developer_cmds

class TestRules(CommandTest):

    character_typeclass = Character

    def test_stat_modifiers(self):
        #initialize stat modifier cache
        self.char1.at_init()
        self.char2.at_init()
        # check that stats mods are at correct value for stats all being max 100
        command = developer_cmds.CmdViewObj
        arg = " =stat_cache"
        wanted_message = "Character ID: 6 STR_dodge_mod: 33|Character ID: 6 STR_action_mod: 20|Character ID: 6 STR_action_cost_mod: 0.25|Character ID: 6 STR_dmg_mod: 4|Character ID: 6 CON_dodge_mod: 33|Character ID: 6 CON_action_mod: 20|Character ID: 6 CON_action_cost_mod: 0.25|Character ID: 6 CON_dmg_mod: 4|Character ID: 6 OBS_dodge_mod: 33|Character ID: 6 OBS_action_mod: 20|Character ID: 6 OBS_action_cost_mod: 0.25|Character ID: 6 OBS_dmg_mod: 4|Character ID: 6 AGI_dodge_mod: 33|Character ID: 6 AGI_action_mod: 20|Character ID: 6 AGI_action_cost_mod: 0.25|Character ID: 6 AGI_dmg_mod: 4|Character ID: 6 SPD_dodge_mod: 33|Character ID: 6 SPD_action_mod: 20|Character ID: 6 SPD_action_cost_mod: 0.25|Character ID: 6 SPD_dmg_mod: 4|Character ID: 6 INT_dodge_mod: 33|Character ID: 6 INT_action_mod: 20|Character ID: 6 INT_action_cost_mod: 0.25|Character ID: 6 INT_dmg_mod: 4|Character ID: 6 WIS_dodge_mod: 33|Character ID: 6 WIS_action_mod: 20|Character ID: 6 WIS_action_cost_mod: 0.25|Character ID: 6 WIS_dmg_mod: 4|Character ID: 6 CHR_dodge_mod: 33|Character ID: 6 CHR_action_mod: 20|Character ID: 6 CHR_action_cost_mod: 0.25|Character ID: 6 CHR_dmg_mod: 4|Character ID: 6 hp_max_mod: 33|Character ID: 6 endurance_max_mod: 33|Character ID: 6 sanity_max_mod: 33|Character ID: 6 load_max_mod: 100|Character ID: 6 busy_mod: 0.25|Character ID: 6 stunned_mod: 0.25|Character ID: 6 purchase_mod: 0.25"
        self.call(command(), arg, wanted_message)
