from evennia.accounts.tests import *
from evennia.commands.tests import *
from evennia.commands.default.tests import *
from evennia.comms.tests import *
from evennia.locks.tests import *

from evennia.commands.default import system, help, building, admin
from evennia.commands.default.cmdset_character import CharacterCmdSet
from django.conf import settings

from typeclasses.races import Human
from typeclasses.exits import Exit
from typeclasses.rooms import Room
from typeclasses.objects import Object
from commands.standard_cmds import StandardCmdsCmdSet


class TestLockfuncs(TestLockfuncs):
    def test_has_account(self):
        self.account.puppet_object(self.session, self.char1)
        self.assertEqual(True, lockfuncs.has_account(self.char1, None))
        self.assertEqual(False, lockfuncs.has_account(self.obj1, None))


class TestDefaultAccountEv(TestDefaultAccountEv):
    def test_puppet_success(self):
        self.account.msg = MagicMock()
        with patch("evennia.accounts.accounts._MULTISESSION_MODE", 2):
            self.account.puppet_object(self.session, self.char1)
            self.account.puppet_object(self.session, self.char1)
            self.account.msg.assert_called_with("You are already puppeting this object.")


class TestHelp(TestHelp):
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    def test_help(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(help.CmdHelp(), "", "Command help entries", cmdset=StandardCmdsCmdSet())

    def test_set_help(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(
            help.CmdSetHelp(),
            "testhelp, General = This is a test",
            "Topic 'testhelp' was successfully created.",
        )
        self.call(help.CmdHelp(), "testhelp", "Help for testhelp", cmdset=CharacterCmdSet())


class TestSystem(TestSystem):
    def test_py(self):
        self.account.puppet_object(self.session, self.char1)
        # we are not testing CmdReload, CmdReset and CmdShutdown, CmdService or CmdTime
        # since the server is not running during these tests.
        self.call(system.CmdPy(), " 1+2", ">>> 1+2|3")
        self.call(system.CmdPy(), "/clientraw 1+2", ">>> 1+2|3")

    def test_scripts(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(system.CmdScripts(), "", "dbref ")

    def test_objects(self):
        self.call(system.CmdObjects(), "", "Object subtype totals")

    def test_about(self):
        self.call(system.CmdAbout(), "", None)

    def test_server_load(self):
        self.call(system.CmdServerLoad(), "", "Server CPU and Memory load:")


class TestAccount(TestAccount):
    def test_ooc_look(self):
        self.account.puppet_object(self.session, self.char1)
        if settings.MULTISESSION_MODE < 2:
            self.call(
                account.CmdOOCLook(), "", "You are out-of-character (OOC).", caller=self.account
            )
        if settings.MULTISESSION_MODE == 2:
            self.call(
                account.CmdOOCLook(),
                "",
                "Account TestAccount (you are Out-of-Character)",
                caller=self.account,
            )

    def test_quell(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(
            account.CmdQuell(),
            "",
            "Quelling to current puppet's permissions (developer).",
            caller=self.account,
        )
    def test_ooc(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(account.CmdOOC(), "", "You go OOC.", caller=self.account)


class TestAdmin(TestAdmin):
    object_typeclass = Object
    character_typeclass = Human
    exit_typeclass = Exit
    room_typeclass = Room
    def test_force(self):
        self.account.puppet_object(self.session, self.char1)
        self.char1.usdesc = 'Char'
        self.char2.usdesc = 'Char2'
        cid = self.char2.id
        self.call(
            admin.CmdForce(),
            "Char2=say test",
            f'Char2(#{cid}) says, "test"|You have forced Char2 to: say test'
        )


class TestBuilding(TestBuilding):
    def test_typeclass(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(building.CmdTypeclass(), "", "Usage: ")
        self.call(
            building.CmdTypeclass(),
            "Obj = evennia.objects.objects.DefaultExit",
            "Obj changed typeclass from evennia.objects.objects.DefaultObject "
            "to evennia.objects.objects.DefaultExit.",
        )
        self.call(
            building.CmdTypeclass(),
            "Obj2 = evennia.objects.objects.DefaultExit",
            "Obj2 changed typeclass from evennia.objects.objects.DefaultObject "
            "to evennia.objects.objects.DefaultExit.",
            cmdstring="swap",
        )
        self.call(building.CmdTypeclass(), "/list Obj", "Core typeclasses")
        self.call(
            building.CmdTypeclass(),
            "/show Obj",
            "Obj's current typeclass is 'evennia.objects.objects.DefaultExit'",
        )
        self.call(
            building.CmdTypeclass(),
            "Obj = evennia.objects.objects.DefaultExit",
            "Obj already has the typeclass 'evennia.objects.objects.DefaultExit'. Use /force to override.",
        )
        self.call(
            building.CmdTypeclass(),
            "/force Obj = evennia.objects.objects.DefaultExit",
            "Obj updated its existing typeclass ",
        )
        self.call(building.CmdTypeclass(), "Obj = evennia.objects.objects.DefaultObject")
        self.call(
            building.CmdTypeclass(),
            "/show Obj",
            "Obj's current typeclass is 'evennia.objects.objects.DefaultObject'",
        )
        self.call(
            building.CmdTypeclass(),
            "Obj",
            "Obj updated its existing typeclass (evennia.objects.objects.DefaultObject).\n"
            "Only the at_object_creation hook was run (update mode). Attributes set before swap were not removed.",
            cmdstring="update",
        )
        self.call(
            building.CmdTypeclass(),
            "/reset/force Obj=evennia.objects.objects.DefaultObject",
            "Obj updated its existing typeclass (evennia.objects.objects.DefaultObject).\n"
            "All object creation hooks were run. All old attributes where deleted before the swap.",
        )

    def test_script(self):
        self.account.puppet_object(self.session, self.char1)
        self.call(building.CmdScript(), "Obj = ", "No scripts defined on Obj")
        self.call(
            building.CmdScript(), "Obj = scripts.Script", "Script scripts.Script successfully added"
        )
        self.call(building.CmdScript(), "", "Usage: ")
        self.call(
            building.CmdScript(),
            "= Obj",
            "To create a global script you need scripts/add <typeclass>.",
        )
        self.call(building.CmdScript(), "Obj ", "dbref ")

        self.call(
            building.CmdScript(), "/start Obj", "0 scripts started on Obj"
        )  # because it's already started
        self.call(building.CmdScript(), "/stop Obj", "Stopping script")

        self.call(
            building.CmdScript(), "Obj = scripts.Script", "Script scripts.Script successfully added"
        )
        self.call(
            building.CmdScript(),
            "/start Obj = scripts.Script",
            "Script scripts.Script could not be (re)started.",
        )
        self.call(
            building.CmdScript(),
            "/stop Obj = scripts.Script",
            "Script stopped and removed from object.",
        )

    def test_teleport(self):
        oid = self.obj1.id
        rid = self.room1.id
        rid2 = self.room2.id
        self.account.puppet_object(self.session, self.char1)
        self.call(building.CmdTeleport(), "", "Usage: ")
        self.call(building.CmdTeleport(), "Obj = Room", "Obj is already at Room.")
        self.call(
            building.CmdTeleport(),
            "Obj = NotFound",
            "Could not find 'NotFound'.|Destination not found.",
        )
        self.call(
            building.CmdTeleport(),
            "Obj = Room2",
            "Obj(#{}) is leaving Room(#{}), heading for Room2(#{}).|Teleported Obj -> Room2.".format(
                oid, rid, rid2
            ),
        )
        self.call(building.CmdTeleport(), "NotFound = Room", "Could not find 'NotFound'.")
        self.call(
            building.CmdTeleport(), "Obj = Obj", "You can't teleport an object inside of itself!"
        )

        self.call(building.CmdTeleport(), "/tonone Obj2", "Teleported Obj2 -> None-location.")
        self.call(building.CmdTeleport(), "/quiet Room2", "Room2(#{})".format(rid2))
        self.call(
            building.CmdTeleport(),
            "/t",  # /t switch is abbreviated form of /tonone
            "Cannot teleport a puppeted object (Char, puppeted by TestAccount",
        )
        self.call(
            building.CmdTeleport(),
            "/l Room2",  # /l switch is abbreviated form of /loc
            "Destination has no location.",
        )
        self.call(
            building.CmdTeleport(),
            "/q me to Room2",  # /q switch is abbreviated form of /quiet
            "Char is already at Room2.",
        )

    def test_tunnel(self):
        self.call(building.CmdTunnel(), "n = TestRoom2;test2", "Created room TestRoom2")
        self.call(building.CmdTunnel(), "", "Usage: ")
        self.call(building.CmdTunnel(), "foo = TestRoom2;test2", "tunnel can only understand the")
        self.call(building.CmdTunnel(), "/tel e = TestRoom3;test3", "Created room TestRoom3")
        Room.objects.get_family(db_key="TestRoom3")
        exits = DefaultExit.objects.filter_family(db_key__in=("east", "west"))
        self.assertEqual(len(exits), 2)

    def test_spawn(self):
        def get_object(commandTest, obj_key):
            # A helper function to get a spawned object and
            # check that it exists in the process.
            query = search_object(obj_key)
            commandTest.assertIsNotNone(query)
            commandTest.assertTrue(bool(query))
            obj = query[0]
            commandTest.assertIsNotNone(obj)
            return obj

        self.account.puppet_object(self.session, self.char1)

        # Tests "spawn" without any arguments.
        self.call(building.CmdSpawn(), " ", "Usage: spawn")

        # Tests "spawn <prototype_dictionary>" without specifying location.

        self.call(
            building.CmdSpawn(),
            "/save {'prototype_key': 'testprot', 'key':'Test Char', "
            "'typeclass':'evennia.objects.objects.DefaultCharacter'}",
            "Saved prototype: testprot",
            inputs=["y"],
        )

        self.call(
            building.CmdSpawn(),
            "/save testprot2 = {'key':'Test Char', "
            "'typeclass':'evennia.objects.objects.DefaultCharacter'}",
            "(Replacing `prototype_key` in prototype with given key.)|Saved prototype: testprot2",
            inputs=["y"],
        )

        self.call(building.CmdSpawn(), "/search ", "Key ")
        self.call(building.CmdSpawn(), "/search test;test2", "No prototypes found.")

        self.call(
            building.CmdSpawn(),
            "/save {'key':'Test Char', " "'typeclass':'evennia.objects.objects.DefaultCharacter'}",
            "A prototype_key must be given, either as `prototype_key = <prototype>` or as "
            "a key 'prototype_key' inside the prototype structure.",
        )

        self.call(building.CmdSpawn(), "/list", "Key ")
        self.call(building.CmdSpawn(), "testprot", "Spawned Test Char")

        # Tests that the spawned object's location is the same as the character's location, since
        # we did not specify it.
        testchar = get_object(self, "Test Char")
        self.assertEqual(testchar.location, self.char1.location)
        testchar.delete()

        # Test "spawn <prototype_dictionary>" with a location other than the character's.
        spawnLoc = self.room2
        if spawnLoc == self.char1.location:
            # Just to make sure we use a different location, in case someone changes
            # char1's default location in the future...
            spawnLoc = self.room1

        self.call(
            building.CmdSpawn(),
            "{'prototype_key':'GOBLIN', 'typeclass':'evennia.objects.objects.DefaultCharacter', "
            "'key':'goblin', 'location':'%s'}" % spawnLoc.dbref,
            "Spawned goblin",
        )
        goblin = get_object(self, "goblin")
        # Tests that the spawned object's type is a DefaultCharacter.
        self.assertIsInstance(goblin, DefaultCharacter)
        self.assertEqual(goblin.location, spawnLoc)

        goblin.delete()

        # create prototype
        protlib.create_prototype(
            {
                "key": "Ball",
                "typeclass": "evennia.objects.objects.DefaultCharacter",
                "prototype_key": "testball",
            }
        )

        # Tests "spawn <prototype_name>"
        self.call(building.CmdSpawn(), "testball", "Spawned Ball")

        ball = get_object(self, "Ball")
        self.assertEqual(ball.location, self.char1.location)
        self.assertIsInstance(ball, DefaultObject)
        ball.delete()

        # Tests "spawn/n ..." without specifying a location.
        # Location should be "None".
        self.call(
            building.CmdSpawn(), "/n 'BALL'", "Spawned Ball"
        )  # /n switch is abbreviated form of /noloc
        ball = get_object(self, "Ball")
        self.assertIsNone(ball.location)
        ball.delete()

        self.call(
            building.CmdSpawn(),
            "/noloc {'prototype_parent':'TESTBALL', 'prototype_key': 'testball', 'location':'%s'}"
            % spawnLoc.dbref,
            "Error: Prototype testball tries to parent itself.",
        )

        # Tests "spawn/noloc ...", but DO specify a location.
        # Location should be the specified location.
        self.call(
            building.CmdSpawn(),
            "/noloc {'prototype_parent':'TESTBALL', 'key': 'Ball', 'prototype_key': 'foo', 'location':'%s'}"
            % spawnLoc.dbref,
            "Spawned Ball",
        )
        ball = get_object(self, "Ball")
        self.assertEqual(ball.location, spawnLoc)
        ball.delete()

        # test calling spawn with an invalid prototype.
        self.call(building.CmdSpawn(), "'NO_EXIST'", "No prototype named 'NO_EXIST' was found.")

        # Test listing commands
        self.call(building.CmdSpawn(), "/list", "Key ")

        # spawn/edit (missing prototype)
        # brings up olc menu
        msg = self.call(building.CmdSpawn(), "/edit")
        assert "Prototype wizard" in msg

        # spawn/edit with valid prototype
        # brings up olc menu loaded with prototype
        msg = self.call(building.CmdSpawn(), "/edit testball")
        assert "Prototype wizard" in msg
        assert hasattr(self.char1.ndb._menutree, "olc_prototype")
        assert (
            dict == type(self.char1.ndb._menutree.olc_prototype)
            and "prototype_key" in self.char1.ndb._menutree.olc_prototype
            and "key" in self.char1.ndb._menutree.olc_prototype
            and "testball" == self.char1.ndb._menutree.olc_prototype["prototype_key"]
            and "Ball" == self.char1.ndb._menutree.olc_prototype["key"]
        )
        assert "Ball" in msg and "testball" in msg

        # spawn/edit with valid prototype (synomym)
        msg = self.call(building.CmdSpawn(), "/edit BALL")
        assert "Prototype wizard" in msg
        assert "Ball" in msg and "testball" in msg

        # spawn/edit with invalid prototype
        msg = self.call(
            building.CmdSpawn(), "/edit NO_EXISTS", "No prototype named 'NO_EXISTS' was found."
        )

        # spawn/examine (missing prototype)
        # lists all prototypes that exist
        self.call(building.CmdSpawn(), "/examine", "You need to specify a prototype-key to show.")

        # spawn/examine with valid prototype
        # prints the prototype
        msg = self.call(building.CmdSpawn(), "/examine BALL")
        assert "Ball" in msg and "testball" in msg

        # spawn/examine with invalid prototype
        # shows error
        self.call(
            building.CmdSpawn(), "/examine NO_EXISTS", "No prototype named 'NO_EXISTS' was found."
        )
