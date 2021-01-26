from evennia.commands.default.tests import CommandTest
from commands import developer_cmds
from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from evennia import create_object
from typeclasses.equipment import clothing
from commands import standard_cmds
from typeclasses.equipment.wieldable import OneHandedWeapon


class TestCommands(CommandTest):

    """
        CommandTest.call arguments
        call(cmdobj, args, msg=None, cmdset=None,
            noansi=True, caller=None, receiver=None, cmdstring=None,
            obj=None, inputs=None, raw_string=None,
        ):
    Objects in EvenniaTest
        self.obj1 = obj
        self.obj2 = "obj2"
        self.char1 = "char"
        self.char2 = "char2"
        self.exit = "out"
    """
    # account_typeclass = DefaultAccount
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    # script_typeclass = DefaultScript

    def test_cmds(self):

        # make character names something easy to tell apart
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'
        # make objects targetable for testing
        self.obj1.targetable = True
        self.obj2.targetable = True
        self.obj3 = create_object(Object, key="Obj3")
        self.obj3.targetable = True
        self.obj3.location = self.char1.location
        self.sword = create_object(OneHandedWeapon, key="a sword")
        self.sword.targetable = True
        self.sword.location = self.char1.location

    # misc command test
        # provide a target that does not exist with a command requiring a target
        #command = developer_cmds.CmdMultiCmd
        #arg = "= wear none existant object"
        #wanted_message = "none existant object is not here."
        #self.call(command(), arg, wanted_message)

    # test deffering commands
        # defer a command and complete it
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, complete_cmd_early"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command."
        self.call(command(), arg, wanted_message)

        # request a deffered command to stop
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # you can not fullow up a busy command with another busy command
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, defer_cmd"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|You will be busy for 5 seconds."
        self.call(command(), arg, wanted_message)

        # force a deffered command to stop, a deffered command was left open on 'char' from the test above
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_cmd"
        wanted_message = "You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # request the stop of a deffered command on self when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd"
        wanted_message = "You may want to test_cmd.|You are not commited to an action."
        self.call(command(), arg, wanted_message)

        # complete a command early when there is none
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wanted_message = "You are not commited to an action."
        self.call(command(), arg, wanted_message)

        # request the stop of a deffered command on a target that has no deffered command
        command = developer_cmds.CmdMultiCmd
        arg = "= interrupt_cmd Char2, l"
        wanted_message = "Char2 is not commited to an action."
        self.call(command(), arg, wanted_message)

        # request target to stop a deffered comamnd
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd, interrupt_cmd, y"
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command.|Stop your defer_cmd command to test_cmd? 'y' for yes or 'i' to ignore.|You are no longer busy.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # stun a character and stop it early
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, stop_stun"
        wanted_message = "You will be stunned for 3 seconds.|You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wanted_message)

        # stun locks out busy commands
        command = developer_cmds.CmdMultiCmd
        arg = "= stun_self, defer_cmd"
        wanted_message = "You will be stunned for 3 seconds.|You will be stunned for 3 seconds."
        self.call(command(), arg, wanted_message)

        # stop a stun on self when there is no stun
        command = developer_cmds.CmdMultiCmd
        arg = "= stop_stun"
        wanted_message = "You are no longer stunned.|Stunned stopped message successful.|Test command ran successfully."
        self.call(command(), arg, wanted_message)  # stop the stun above
        wanted_message = "You are not currently stunned."
        self.call(command(), arg, wanted_message)

    # test punch, kick and dodge
        # test punch
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade \\d+: You punch at Char2.*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test kick
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade \\d+: You kick at Char2'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test dodge
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge, control_other Char2=punch Char, complete_cmd_early Char2"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily.\nFacing Char Char2 pulls theirs hand back preparing an attack.\nYou are no longer busy.\nYou try to dodge the incoming attack.\nevade \d+ VS punch \d+: Char2 punches at you with their fist "
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test attacking an Object
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Obj, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Obj Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade \\d+: You punch at Obj'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test a target leaving melee range
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char2, control_other Char2=out, complete_cmd_early"
        wanted_message = "You can no longer reach Char2\\."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # get Char2 back into the room.
        self.char2.location = self.room1
        self.assertEqual(self.char2.location, self.room1)

        # test commands that can not target self
        command = developer_cmds.CmdMultiCmd
        arg = "= punch Char"
        wanted_message = 'You can not punch yourself.'
        cmd_result = self.call(command(), arg, wanted_message)

        # test attaking an exit that is not targetable
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out"
        wanted_message = 'You can not punch out.'
        cmd_result = self.call(command(), arg, wanted_message)

        # test attaking a targetable exit
        self.exit.targetable = True
        command = developer_cmds.CmdMultiCmd
        arg = "= punch out, complete_cmd_early"
        wanted_message = "You will be busy for \\d+ seconds.\nFacing out Char pulls theirs hand back preparing an attack.\npunch \\d+ VS evade 5: You punch at out"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        self.exit.targetable = False

        # test a targeted command that has a stop_request against an object
        command = developer_cmds.CmdMultiCmd
        arg = "= kick Obj, complete_cmd_early"
        wanted_message = "You will be busy for \\d+ seconds.\nFacing Obj Char lifts theirs knee up preparing an attack.\nkick \\d+ VS evade 5: You kick at Obj"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

    # test one_handed skillset
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wanted_message = "You pick up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= wield sword"
        wanted_message = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test the stab command
        command = developer_cmds.CmdMultiCmd
        arg = "= stab char2, complete_cmd_early"
        wanted_message = 'You will be busy for \\d+ seconds.\nFacing Char2 Char raises a sword preparing an attack.\nstab \\d+ VS evade \\d+: You stab at Char2.*'
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        arg = "= drop sword"
        wanted_message = "You drop a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)

    # test clothing commands
        # test character with empty inventory
        command = developer_cmds.CmdMultiCmd
        arg = "= inv, complete_cmd_early"
        wanted_message = "You are not carrying or wearing anything."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain it takes time to search inventory
        command = developer_cmds.CmdMultiCmd
        arg = "= inv, complete_cmd_early"
        wanted_message = "You rummage through your possessions, taking inventory"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Make a test hat
        test_hat = create_object(clothing.Clothing, key="test hat")
        test_hat.db.clothing_type = "hat"
        test_hat.location = self.room1
        # Make a test shirt
        test_shirt = create_object(clothing.Clothing, key="test shirt")
        test_shirt.db.clothing_type = "top"
        test_shirt.location = self.char1
        # Make a test helmet
        test_helmet = create_object(clothing.HumanoidArmor, key="test helmet")
        test_helmet.db.clothing_type = "head"
        test_helmet.at_init()  # TestCommands will not call at_init hooks.
        test_helmet.location = self.char1
        # give the helmet an armor rating
        test_helmet.dr.PRC = 2
        test_helmet.dr.ACD = 3
        self.assertEqual(test_helmet.attributes.get('dr_PRC'), 2)
        self.assertEqual(test_helmet.dr.PRC, 2)
        # Test wear with no arguments.
        command = developer_cmds.CmdMultiCmd
        arg = "= wear"
        wanted_message = "What would you like to wear?|If you need help try help wear."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test wearing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= get hat, complete_cmd_early"
        wanted_message = "You pick up test hat"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain the hat is no longer in hand
        self.assertFalse(self.char1.is_holding(test_hat))
        # Test tring to wear an item not on person also tests Command.search_caller_only
        command = developer_cmds.CmdMultiCmd
        arg = "= wear Obj"
        wanted_message = "Try picking it up first with get Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test tring to wear an item that is not clothing, also tests target_inherits_from
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj, complete_cmd_early"
        wanted_message = "You pick up Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain hands are occupied with the object picked up
        self.assertTrue(self.char1.is_holding(self.obj1))
        # test getting an object already in possession
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj"
        wanted_message = "You are already carrying Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test getting an object when hands are already full
        command = developer_cmds.CmdMultiCmd
        arg = "= get Obj2, complete_cmd_early"
        wanted_message = "You pick up Obj2"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= get Obj3, complete_cmd_early"
        wanted_message = "Your hands are full."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= drop Obj2"
        wanted_message = "You drop Obj2"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain hands are NOT occupied with the object dropped
        self.assertFalse(self.char1.is_holding(self.obj2))
        # test wearing an object that is not clothing
        arg = "= wear Obj"
        wanted_message = "You can only wear clothing and armor."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= drop Obj"
        wanted_message = "You drop Obj."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        self.assertFalse(self.char1.is_holding(self.obj1))
        # test removing an item
        command = developer_cmds.CmdMultiCmd
        arg = "= remove hat, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar removes test hat.\nYou are no longer busy.\nChar allowed you to complete your remove command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Put the hat back on to test covering
        command = developer_cmds.CmdMultiCmd
        arg = "= wear hat, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test hat.\nChar puts on test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test wearing a peace of armor
        command = developer_cmds.CmdMultiCmd
        arg = "= wear helmet, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test helmet.\nChar puts on test helmet, covering test hat.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test character with items worn and not
        command = developer_cmds.CmdMultiCmd
        arg = "= inv, complete_cmd_early"
        wanted_message = "You are carrying:\n test shirt   \r\nYou are wearing:\n test helmet   \n test hat"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        #misc tests
        self.assertEqual(test_hat.db.worn, True)
        self.assertEqual(test_hat.db.clothing_type, 'hat')
        self.assertEqual(test_helmet.db.clothing_type, "head")
        self.assertTrue('head' in test_helmet.type_limit)
        # Make certain return_appearance is working
        self.assertEqual(self.char1.return_appearance(self.char1), "You are wearing test helmet.")
        # Test now with the look command
        command = developer_cmds.CmdMultiCmd
        arg = "= l me"
        wanted_message = "You are wearing test helmet."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test clothing covering.
        # Make a test shirt
        test_undershirt = create_object(clothing.Clothing, key="test undershirt")
        test_undershirt.db.clothing_type = "undershirt"
        test_undershirt.location = self.char1
        # Test wearing the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear undershirt, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test undershirt.\nChar puts on test undershirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test wearing the shirt covering the undershirt
        command = developer_cmds.CmdMultiCmd
        arg = "= wear shirt, complete_cmd_early"
        wanted_message = "You will be busy for 1 second.\nYou begin to put on test shirt.\nChar puts on test shirt, covering test undershirt.\nYou are no longer busy.\nChar allowed you to complete your wear command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        self.assertEqual(test_undershirt.db.covered_by, test_shirt)
        #verify that the helmet's armor rating has been cached in the wearer
        self.assertEqual(self.char1.body.head.dr.PRC, 2)
        self.assertEqual(self.char1.body.head.dr.ACD, 3)
        self.assertEqual(self.char1.body.head.dr.BLG, 0)
        # test dropping a worn item
        arg = "= drop shirt"
        wanted_message = 'You must remove test shirt to drop it.\r\nTry command remove test shirt to remove it.'
        self.call(command(), arg, wanted_message, caller=self.char1)

        # test wielding
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wanted_message = "You pick up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= wield sword"
        wanted_message = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain wield worked
        items_equipped = self.char1.wielding()
        self.assertTrue(self.sword in items_equipped)
        # verify dropping the sword stops it from being wielded
        arg = "= drop sword"
        wanted_message = "You drop a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        # test the unwield command
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wanted_message = "You pick up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= unwield sword"
        wanted_message = "You are not wielding a sword."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain the sword is in hand
        self.assertTrue(self.char1.is_holding(self.sword))
        arg = "= wield sword"
        wanted_message = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        items_equipped = self.char1.wielding()
        self.assertTrue(self.sword in items_equipped)
        arg = "= unwield sword"
        wanted_message = "You stop wielding a sword."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        arg = "= drop sword"
        wanted_message = "You drop a sword"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain it is not wielded after dropping
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        # make certain wield & unwield room messages are correct
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wanted_message = "Char picks up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        arg = "= wield sword"
        wanted_message = "Char wields a sword"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        items_equipped = self.char1.wielding()
        self.assertTrue(self.sword in items_equipped)
        arg = "= unwield sword"
        wanted_message = "Char stops wielding a sword."
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        items_equipped = self.char1.wielding()
        self.assertFalse(self.sword in items_equipped)
        #verify an item deleted while held and or wielded will automatically be removed from hand.
        arg = "= wield sword"
        wanted_message = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        sword_dbref = self.sword.dbref
        self.sword.delete()
        self.assertFalse(self.char1.wielding())
        hands_state = self.char1.hands()
        self.assertNotEqual(hands_state[0].occupied, sword_dbref)
        self.assertNotEqual(hands_state[1].occupied, sword_dbref)
        # remake the sword
        self.sword = create_object(OneHandedWeapon, key="a sword")
        self.sword.targetable = True
        self.sword.location = self.char1.location

        # test method get_body_part
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, char2"
        wanted_message = r"get_body_part returned: False"
        cmd_result = self.call(command(), arg)
        self.assertFalse(cmd_result == wanted_message)
        # now test an object with no body parts
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r get_body_part, obj"
        wanted_message = r"^get_body_part returned: False"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # test method damage after damage reduction
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 3, None, head"
        wanted_message = "dmg_after_dr returned: 1"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # make certain the lowest number returned is 0
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 0, None, head"
        wanted_message = "dmg_after_dr returned: 0"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # now change the targets dr to make certain that affects
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 3, None, head"
        wanted_message = "dmg_after_dr returned: 0"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # Verify giving None as dmg_dealt works
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = None, None, head"
        wanted_message = r"dmg_after_dr returned: \d+"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # Verify max_defense works
        # Verify Command.dmg_type.TYPE value, adds to attack damage
        # testing char.dr and the worn helmet.dr
        # In this case ACD defense is 6
        #    is the highest defense value vs Command.cmd_types.ACD value of 1 (adds to damage)
        self.char1.dr.ACD = 3
        self.char1.dr.PRC = 1
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char = 7, True, head"
        wanted_message = r"dmg_after_dr returned: 2"
        cmd_result = self.call(command(), arg, wanted_message)
        # test adding a weapon to the equation
        self.sword.dmg_types.ACD = 1
        command = developer_cmds.CmdMultiCmd
        arg = "= get sword, complete_cmd_early"
        wanted_message = "Char picks up a sword"
        cmd_result = self.call(command(), arg, caller=self.char1, receiver=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdMultiCmd
        arg = "= wield sword"
        wanted_message = "You wield a sword in your"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "/r dmg_after_dr, char, requires_wielding:True, cmd_type:one_handed = 7, True, head"
        wanted_message = r"dmg_after_dr returned: 3"
        cmd_result = self.call(command(), arg, wanted_message)
        # change the sword's ACD modifier, damage should change by the adjustment
        self.sword.dmg_types.ACD = 2
        wanted_message = r"dmg_after_dr returned: 4"
        self.call(command(), arg, wanted_message)
        # Test item.act_roll_max_mod
        self.sword.act_roll_max_mod = 1
        command = developer_cmds.CmdCmdAttrTest
        arg = "requires_wielding:True, cmd_type:one_handed=roll_max"
        wanted_message = r"roll_max: 51"
        self.call(command(), arg, wanted_message)
        self.sword.act_roll_max_mod = 10
        wanted_message = r"roll_max: 60"
        self.call(command(), arg, wanted_message)
        # test item evasion bonus
        self.assertFalse(self.sword.attributes.has('evd_stats'))
        self.sword.evd_stats = ('AGI',)
        self.assertEqual(self.sword.attributes.get('evd_stats'), ('AGI',))
        self.sword.evd_roll_max_mod = 1
        self.assertEqual(self.sword.attributes.get('evd_roll_max_mod'), 1)
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge, control_other Char2=punch Char, complete_cmd_early Char2"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily.\nFacing Char Char2 pulls theirs hand back preparing an attack.\nYou are no longer busy.\nYou try to dodge the incoming attack.\nevade \d+ VS punch \d+: Char2 punches at you with their fist "
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        # defer an evasion command to test
        command = developer_cmds.CmdMultiCmd
        arg = "= dodge"
        wanted_message = r"You will be busy for \d+ seconds.\nYou begin to sway warily."
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdCmdFuncTest
        arg = "evade_roll, self, cmd_type:evasion, evade_mod_stat:AGI = AGI, False, True"
        wanted_message = r"roll_max: 53"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)
        del self.sword.evd_stats
        self.assertFalse(self.sword.attributes.has('evd_stats'))
        del self.sword.evd_roll_max_mod
        self.assertFalse(self.sword.attributes.get('evd_roll_max_mod'))

        # test sit stand lay also tests Character.set_position
        command = developer_cmds.CmdMultiCmd
        arg = "= sit, complete_cmd_early"
        wanted_message = r"You will be busy for \d+ second.|You move to sit down.|You sit down.|You are no longer busy.|Char allowed you to complete your sit command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test other sitting down
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=sit, complete_cmd_early char2"
        wanted_message = "Char2 moves to sit down.|Char2 sits down."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"Char2\(#7\) is sitting here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test character already sitting
        command = developer_cmds.CmdMultiCmd
        arg = "= sit"
        wanted_message = "You are already sitting."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        # stand up
        command = developer_cmds.CmdMultiCmd
        arg = "= stand, complete_cmd_early"
        wanted_message = r"You will be busy for \d+ seconds.|You move to stand up.|You stand up.|You are no longer busy.|Char allowed you to complete your stand command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test other standing
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=stand, complete_cmd_early char2"
        wanted_message = "Char2 moves to stand up.|Char2 stands up."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"Char2\(#7\) is standing here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test character already standing
        command = developer_cmds.CmdMultiCmd
        arg = "= stand"
        wanted_message = "You are already standing."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        # lay down
        command = developer_cmds.CmdMultiCmd
        arg = "= lay, complete_cmd_early"
        wanted_message = r"You will be busy for \d+ second.|You move to lay down.|You lay down.|You are no longer busy.|Char allowed you to complete your lay command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test other laying
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=lay, complete_cmd_early char2"
        wanted_message = "Char2 moves to lay down.|Char2 lays down."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"Char2\(#7\) is laying here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test character already laying
        command = developer_cmds.CmdMultiCmd
        arg = "= lay"
        wanted_message = "You are already laying."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        # a prone Character can not move.
        command = developer_cmds.CmdMultiCmd
        arg = "= out"
        wanted_message = "You must stand up first."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        # stand both characters up
        command = developer_cmds.CmdMultiCmd
        arg = "= stand, complete_cmd_early"
        wanted_message = "You will be busy for 3 seconds.|You move to stand up.|You stand up.|You are no longer busy.|Char allowed you to complete your stand command early with their complete_cmd_early command."
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        self.char2.position = 'standing'
        self.assertEqual(self.char2.position, 'standing')

        # test permision lock down for pose, sdesc and mask
        # test commands on a character without the permission
        for cmd in ('mask', 'sdesc', 'pose'):
            command = developer_cmds.CmdMultiCmd
            arg = f"= {cmd}"
            wanted_message = f"Command '{cmd}' is not available."
            cmd_result = self.call(command(), arg, caller=self.char2)
            self.assertRegex(cmd_result, wanted_message)
        # on on a character with permission
        # mask
        command = developer_cmds.CmdMultiCmd
        arg = "= mask"
        wanted_message = "Usage: (un)mask sdesc"
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        # pose
        command = developer_cmds.CmdMultiCmd
        arg = "= pose"
        wanted_message = "Usage: pose <pose-text> OR pose obj = <pose-text>"
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)
        # sdesc
        command = developer_cmds.CmdMultiCmd
        arg = "= sdesc"
        wanted_message = "Usage: sdesc <sdesc-text>"
        cmd_result = self.call(command(), arg, wanted_message, caller=self.char1)

        # test rpsytem commands
        # emote
        command = developer_cmds.CmdMultiCmd
        arg = "= emote test emote"
        wanted_message = "Char2 test emote."
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # veryfy emote echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other char2=emote test emote"
        wanted_message = "Char2 test emote."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # say
        command = developer_cmds.CmdMultiCmd
        arg = "= say test message"
        wanted_message = r"You say, \"test message\""
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # verify say echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other Char2=say test message"
        wanted_message = r'Char2\(#7\) says, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test saying to another Character
        command = standard_cmds.CmdSay
        arg = 'to char2 "test message'
        wanted_message = r'You say to Char2, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test saying at another Character
        command = standard_cmds.CmdSay
        arg = 'at char2 "test message'
        wanted_message = r'You say at Char2, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # Test your name is replace with You when you are spoken to
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to char "test message'
        wanted_message = r'Char2 says to you, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # make certain say to replaces targets message with name
        # with multiple targets
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to char and obj "test message'
        wanted_message = r'Char2 says to Obj and you, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # test seeing a say that does not target you.
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=say to obj2 and obj "test message'
        wanted_message = r'Char2 says to Obj2 and Obj, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        arg = '=control_other char2=say at obj2 and obj "test message'
        wanted_message = r'Char2 says at Obj2 and Obj, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)

        # Test whisper
        # say
        # test saying to another Character
        command = developer_cmds.CmdMultiCmd
        arg = '=whisper to char2 "test message'
        wanted_message = 'You whisper to Char2, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # test saying at another Character
        command = developer_cmds.CmdMultiCmd
        arg = '=whisper at char2 "test message'
        wanted_message = 'You whisper at Char2, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # verify say echos to room properly
        command = developer_cmds.CmdMultiCmd
        arg = '= control_other Char2=whisper to obj "test message'
        wanted_message = 'Char2 whispers something to Obj.'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # Test your name is replace with You when you are whispered to
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to char "test message'
        wanted_message = r'Char2 whispers to you, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # make certain whisper to replaces targets message with name
        # with multiple targets
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to char and obj "test message'
        wanted_message = r'Char2 whispers to Obj and you, "test message"'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # test seeing a multi target whisper that does not target you.
        command = developer_cmds.CmdMultiCmd
        arg = '=control_other char2=whisper to obj2 and obj "test message'
        wanted_message = r'Char2 whispers something to Obj2 and Obj.'
        self.call(command(), arg, wanted_message, caller=self.char1)
        arg = '=control_other char2=whisper at obj2 and obj "test message'
        wanted_message = r'Char2 whispers something at Obj2 and Obj.'
        self.call(command(), arg, wanted_message, caller=self.char1)
        # test recog
        command = developer_cmds.CmdMultiCmd
        arg = "= recog Char2 as a test change"
        wanted_message = r"Char will now remember Char2 as a test change."
        self.call(command(), arg, wanted_message, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"a test change\(#7\) is standing here\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdMultiCmd
        arg = "= forget test change"
        wanted_message = r"Char will now know them only as 'Char2'."
        self.call(command(), arg, wanted_message, caller=self.char1)
        # test mask
        command = developer_cmds.CmdMultiCmd
        arg = "= mask test change"
        wanted_message = r"You wear a mask as 'test change [masked]'."
        self.call(command(), arg, wanted_message, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"test change"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdMultiCmd
        arg = "= unmask"
        wanted_message = r"You remove your mask and are again 'Char'."
        self.call(command(), arg, wanted_message, caller=self.char1)
        # test pose
        command = developer_cmds.CmdMultiCmd
        arg = "= pose obj= test pose"
        wanted_message = r"Pose will read 'Obj test pose.'."
        self.call(command(), arg, wanted_message, caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"Obj\(#4\) test pose\."
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdMultiCmd
        arg = "= pose reset obj="
        wanted_message = r"Pose will read 'Obj is here.'."
        self.call(command(), arg, wanted_message, caller=self.char1)

        # test actions against an unconscious characer
        self.char1.set_unconscious()
        self.assertFalse(self.char1.ready())
        command = developer_cmds.CmdMultiCmd
        arg = "= control_other Char2=punch Char, complete_cmd_early Char2"
        wanted_message = r"\nevade 5 VS punch"
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        command = developer_cmds.CmdMultiCmd
        arg = "= out"
        wanted_message = r"You can not do that while unconscious."
        cmd_result = self.call(command(), arg, wanted_message,  caller=self.char1)
        command = developer_cmds.CmdMultiCmd
        # make certain Character's pose shows unconscious
        arg = "= l"
        wanted_message = r"Char is unconscious here"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)
        # wake the character up
        self.char1.set_unconscious(False)
        # make certain Character is in laying position after waking up.
        command = developer_cmds.CmdMultiCmd
        arg = "= l"
        wanted_message = r"Char is laying here"
        cmd_result = self.call(command(), arg, caller=self.char2)
        self.assertRegex(cmd_result, wanted_message)

        # commands that should work when the user is busy
        # defer a command and complete it
        command = developer_cmds.CmdMultiCmd
        arg = "= defer_cmd"
        #|Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command.
        wanted_message = "You will be busy for 5 seconds.|Char is testing deferring a command."
        self.call(command(), arg, wanted_message)
        # commands that should work when the Character is busy
        command = developer_cmds.CmdMultiCmd
        not_req_ready_commands = ('look', 'drop', 'help', 'stat', 'say')
        for non_ready_cmd in not_req_ready_commands:
            arg = f"= {non_ready_cmd}"
            cmd_result = self.call(command(), arg, caller=self.char1)
            self.assertFalse(cmd_result.startswith('You will be busy for'))
        # commands that should not work when the Character is busy
        command = developer_cmds.CmdMultiCmd
        req_ready_commands = ('punch', 'inv', 'out', 'sit', 'stand', 'lay',
                              'get', 'wear', 'remove', 'whisper', 'kick',
                              'dodge')
        for ready_cmd in req_ready_commands:
            arg = f"= {ready_cmd}"
            cmd_result = self.call(command(), arg, caller=self.char1)
            self.assertTrue(cmd_result.startswith('You will be busy for'))
        # comlete your defer command
        command = developer_cmds.CmdMultiCmd
        arg = "= complete_cmd_early"
        wanted_message = "Defered command ran successfully.|You are no longer busy.|Char allowed you to complete your defer_cmd command early with their complete_cmd_early command."
        self.call(command(), arg, wanted_message)

        # test the statistics command
        command = developer_cmds.CmdMultiCmd
        arg = "= stat"
        wanted_message = "Statistics for: Char"
        cmd_result = self.call(command(), arg)
        self.assertRegex(cmd_result, wanted_message)

        # make certain commands have been taking a cost.
        self.assertTrue(self.char1.END < 100)

        # make certain commands can have a numbered target
        test_object1 = create_object(Object, key="object one")
        test_object1.location = self.char1.location
        test_object2 = create_object(Object, key="object two")
        test_object2.location = self.char1.location
        command = developer_cmds.CmdMultiCmd
        arg = "= punch object"
        wanted_message = "You can not punch object one"
        self.call(command(), arg, wanted_message)
        arg = "= punch 2 object"
        wanted_message = "You can not punch object two"
        self.call(command(), arg, wanted_message)
        # test numbered targets and say to commad
        test_object1.targetable = True
        test_object2.targetable = True
        command = standard_cmds.CmdSay
        arg = 'to 2 object "test message'
        wanted_message = r'You say to object two, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # make certain saying to the first object works after saying to the second
        # this makes certain the Command.target is not a global variable
        arg = 'to object "test message'
        wanted_message = r'You say to object one, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # add unit test for drop after get has been updated to use UM targetting system.

        # test for multiple targets using &
        command = standard_cmds.CmdSay
        arg = 'to object & 2 object "test message'
        wanted_message = r'You say to object one and object two, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
        # test for multiple targets using " and "
        command = standard_cmds.CmdSay
        arg = 'to object and 2 object "test message'
        wanted_message = r'You say to object one and object two, "test message"'
        cmd_result = self.call(command(), arg, caller=self.char1)
        self.assertRegex(cmd_result, wanted_message)
