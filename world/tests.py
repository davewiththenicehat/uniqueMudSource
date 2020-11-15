from evennia.commands.default.tests import CommandTest
from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from commands import developer_cmds
from world.rules import body

class TestRules(CommandTest):

    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room

    def test_rules(self):
        """
        Used to test the character object
        stat modifiers unit tests are in world.rules.tests.TestRules.test_stat_modifiers

        Objects in EvenniaTest
            self.obj1 self.obj2 self.char1 self.char2 self.exit
        """
        #initialize stat modifier cache
        self.char1.at_init()
        self.char2.at_init()
        # check that stats mods are at correct value for stats all being max 100
        command = developer_cmds.CmdViewObj
        arg = " =stat_cache"
        wanted_message = "Character ID: 6 STR_evade_mod: 33|Character ID: 6 STR_action_mod: 20|Character ID: 6 STR_action_cost_mod: 0.25|Character ID: 6 STR_dmg_mod: 4|Character ID: 6 CON_evade_mod: 33|Character ID: 6 CON_action_mod: 20|Character ID: 6 CON_action_cost_mod: 0.25|Character ID: 6 CON_dmg_mod: 4|Character ID: 6 OBS_evade_mod: 33|Character ID: 6 OBS_action_mod: 20|Character ID: 6 OBS_action_cost_mod: 0.25|Character ID: 6 OBS_dmg_mod: 4|Character ID: 6 AGI_evade_mod: 33|Character ID: 6 AGI_action_mod: 20|Character ID: 6 AGI_action_cost_mod: 0.25|Character ID: 6 AGI_dmg_mod: 4|Character ID: 6 SPD_evade_mod: 33|Character ID: 6 SPD_action_mod: 20|Character ID: 6 SPD_action_cost_mod: 0.25|Character ID: 6 SPD_dmg_mod: 4|Character ID: 6 INT_evade_mod: 33|Character ID: 6 INT_action_mod: 20|Character ID: 6 INT_action_cost_mod: 0.25|Character ID: 6 INT_dmg_mod: 4|Character ID: 6 WIS_evade_mod: 33|Character ID: 6 WIS_action_mod: 20|Character ID: 6 WIS_action_cost_mod: 0.25|Character ID: 6 WIS_dmg_mod: 4|Character ID: 6 CHR_evade_mod: 33|Character ID: 6 CHR_action_mod: 20|Character ID: 6 CHR_action_cost_mod: 0.25|Character ID: 6 CHR_dmg_mod: 4|Character ID: 6 hp_max_mod: 33|Character ID: 6 endurance_max_mod: 33|Character ID: 6 sanity_max_mod: 33|Character ID: 6 load_max_mod: 100|Character ID: 6 busy_mod: 0.25|Character ID: 6 stunned_mod: 0.25|Character ID: 6 purchase_mod: 0.25"
        self.call(command(), arg, wanted_message)

        # test body.get_part
        #get_part(target, no_underscore=False, log=None)
        body_part = body.get_part(self.char1)
        self.assertTrue(body_part in self.char1.body.parts)
