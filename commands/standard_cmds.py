import time
import math
from datetime import timedelta, datetime

from evennia.utils import evtable, evmore
from evennia.utils.utils import fill, dedent, inherits_from, make_iter, delay
from evennia import default_cmds
from evennia.contrib import rpsystem
from evennia import CmdSet
from evennia.commands.default.help import CmdHelp as EvCmdHelp
from evennia.commands.default.system import CmdObjects
from evennia.commands.default.general import CmdLook as EvCmdLook

from commands.command import Command
from world.rules import stats, skills
from utils.um_utils import highlighter, error_report
from typeclasses.exits import STANDARD_EXITS
from world.rules.body import CHARACTER_CONDITIONS
from world.status_functions import status_delay_get, status_delay_stop


class StandardCmdsCmdSet(default_cmds.CharacterCmdSet):
    """
    Collection of very basic game command.
    That have no specific grouping.
    That must in some way be altered from evennias provided version.
    examples drop, inventory

    Unit tests for these commands are in commands.tests.TestCommands
    """

    priority = 100

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        self.add(CmdDrop)
        self.add(CmdInventory)
        self.add(CmdSit)
        self.add(CmdStand)
        self.add(CmdLay)
        self.add(CmdGet)
        self.add(CmdSay)
        self.add(CmdHelp)
        self.add(CmdLook)
        self.add(CmdWhisper)
        self.add(CmdStatus)
        self.add(UMCmdObjects)
        self.add(CmdPut)
        self.add(CmdCondition)
        self.add(CmdLearn)
        self.add(CmdStop)
        self.add(CmdSkills)
        self.add(CmdEcho)

class CmdEcho(Command):
    """
    echo a message to command caller.

    Notes:
        Message will echo to unconcious or dead Characters also.

    Usage:
        echo [message], echo message to the command's caller.
        Intended for making clickable links in commands that show a message.
    """

    key = 'echo'
    auto_help = False

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # Does the command require the ready status
        self.requires_conscious = False  # if true this command requires the caller to be conscious

    def func(self):
        """
        To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.

        UniqueMud:
            UniqueMud's func will:
                defer the action of the command.
                call Command.start_message if the command deffered successfully.
            If your command does not defer an action, override Command.func
            It is possible to use this method within your overidden one with:
                super().self.func()
        """
        caller = self.caller
        args = self.args
        if args:
            caller.msg(args, force=True)

class CmdSkills(Command):
    """
    Show your skill ranks, experience and experience required for next rank.

    Usage:
        skills, Show all know skills.
        skills [set name], Show skills for only the set name.
    """

    key = 'skills'

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # Does the command require the ready status
        self.requires_conscious = True  # if true this command requires the caller to be conscious

    def func(self):
        """
        To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.

        UniqueMud:
            UniqueMud's func will:
                defer the action of the command.
                call Command.start_message if the command deffered successfully.
            If your command does not defer an action, override Command.func
            It is possible to use this method within your overidden one with:
                super().self.func()
        """
        caller = self.caller
        # check if argument is a skill set name.
        args = self.args.lower().strip().replace(' ', '_') if self.args else None
        #single_set = args if args in caller.skills.skills.keys() else False
        if args:
            if args in caller.skills.skills.keys():
                single_set = args
            else:
                caller.msg(f"{args}, is not a skill set name.")
                msg = "Skill sets are: "
                skill_sets = [*caller.skills.skills.keys()]
                for set_name in skill_sets[:-1]:
                    set_title = set_name.replace('_', ' ')
                    set_title = highlighter(set_title, click_cmd="skills "+set_title)
                    msg += set_title+', '
                set_title = skill_sets[-1].replace('_', ' ')
                set_title = highlighter(set_title, click_cmd="skills "+set_title)
                msg += f"and {set_title.replace('_', ' ')}."
                caller.msg(msg)
                return True
        else: # run as standard skills call
            single_set = False
        # loop through all skills
        for set_name, skill_names in caller.skills.skills.items():
            # if a set name was provided as an argument, show only that set.
            if single_set:
                if set_name != single_set:
                    continue
            skill_set = getattr(caller.skills, set_name, False)  # skill set instance
            skill_points = skill_set.get('skill_points')  # collect skill set's skill points
            # lists to be used as rows in the
            known_skills = []
            known_skills_ranks = []
            known_skills_exp = []
            known_skills_next_rank = []
            # loop through skills in the skill set
            for skill_name in skill_names:
                if skill_name == 'skill_points':
                    continue
                skill_ranks = skill_set[skill_name]
                # if there are ranks in this skill gather data for the skill
                if skill_ranks:
                    # make the skill name clickable to get help on it
                    skill_title = highlighter(skill_name, click_cmd="help "+skill_name)
                    known_skills.append(skill_title)
                    known_skills_ranks.append(skill_set[skill_name])
                    known_skills_exp.append(math.floor(skill_set[skill_name+'_exp']))
                    # get the command instance for the skill
                    for cmd_set in caller.cmdset.get():
                        cmd_inst = cmd_set.get(skill_name)
                        if cmd_inst:
                            break
                    # get exp required for next rank in this skill
                    exp_required = skills.rank_requirement(skill_set[skill_name]+1,
                                                           cmd_inst.learn_diff)
                    known_skills_next_rank.append(exp_required)
            # display the skill if it has ranks or skill points
            if skill_points or known_skills:
                set_list = []
                set_list.append(known_skills)
                set_list.append(known_skills_ranks)
                set_list.append(known_skills_exp)
                set_list.append(known_skills_next_rank)
                # make the set title clickable to get help on it.
                set_title = set_name.replace('_', ' ').capitalize()
                set_title = highlighter(set_title, click_cmd="help "+set_title)
                caller.msg(set_title, force=True)
                caller.msg(f"skill points: {skill_points}", force=True)
                if known_skills:  # only show skills if some are known
                    set_header = ('skill name', 'ranks', 'exp', 'next rank')
                    set_table = evtable.EvTable(*set_header, table=set_list, border=None, pad_left=4)
                    caller.msg(set_table, force=True)
                caller.msg('|/', force=True)
            elif single_set:
                set_title = single_set.replace('_', ' ')
                set_title = highlighter(set_title, click_cmd="help "+set_title)
                caller.msg(f'You do not know skills or have skill points in the {set_title} skill set.')
        return True


class UMCmdObjects(CmdObjects):
    # overidding to remove 'stats' as an alias
    aliases = ["listobjects", "listobjs", "db"]


class CmdStop(Command):
    """
    Stop an action you are currently commited to.

    Usage:
        stop, stops your current action.
    """
    key = 'stop'

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # Does the command require the ready status

    def func(self):
        """
        To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.

        UniqueMud:
            UniqueMud's func will:
                defer the action of the command.
                call Command.start_message if the command deffered successfully.
            If your command does not defer an action, override Command.func
            It is possible to use this method within your overidden one with:
                super().self.func()
        """
        caller = self.caller
        deferred_cmd = caller.nattributes.get('deffered_command')
        if deferred_cmd:
            if deferred_cmd.unstoppable:  # do not stop unstoppable commands
                caller.msg(f'{deferred_cmd.key.capitalize()} can not be stopped.')
            else:  # all other commands can be stopped with stop
                status_delay_stop(caller, 'busy', False)
        else:  # has no action deferred
            caller.msg('You are not commited to an action.')
        return True


class CmdLearn(Command):
    """
    Learn new skill ranks and display available learning.

    A skill takes 30 seconds to study.
    Your Character is busy during this time.

    When your Character has completed studing the skill they will
    then begin to learn it.
    Your Character is not busy while learning. It can interact in the game as
    normal. With one exception. Your Character can not learn more than one
    skill at a time.

    You can not stop a Character from learning once they are done studing.
    As your Character increases in skill ranks new ranks will take longer to learn.

    Usage:
      learn, display skills your Character can currently learn.
      learn [skill name], increase a skill rank.
      learn [skill name]?, Show information about upgrading a single skill.
    """
    key = 'learn'

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # Does the command require the ready status
        self.defer_time = 30  # time is seconds for the command to wait before running

    def increaseable_ranks_msg(self, increaseable_skills):
        """Message caller available skill increase."""
        caller = self.caller
        msg = ""
        caller_learning = caller.learning
        # message for increaseable skills.
        for skill_name in increaseable_skills:
            cmd_suggestion = highlighter("learn "+skill_name,
                                         click_cmd=f"learn {skill_name}")
            learn_time = skills.learn_time(caller, skill_name)
            learn_time = timedelta(seconds=learn_time)
            msg += f"\n{skill_name.capitalize()} is ready for a new rank.\n" \
                   f"It will take {learn_time} to learn this rank.\n" \
                   f"Increase {skill_name} with {cmd_suggestion}."
        # message for skill currently being learned
        if caller_learning:
            msg = self.currently_learning_msg(msg)
        if not msg:
            msg = "None of your skills are ready for a rank increase."
        caller.msg(msg)

    def currently_learning_msg(self, msg):
        caller = self.caller
        caller_learning = caller.learning
        if not caller_learning:
            return msg
        skill_name = caller_learning.get('skill_name')
        rank = caller_learning.get('rank')
        comp_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(caller_learning.get("comp_date")))
        msg += f"\nYou are currently learning {skill_name} to rank {rank}.\n" \
               f"Learning will complete on {comp_date}."
        return msg

    def func(self):
        """
        To more seamlessly support UniqueMud's deffered command system, evennia's Command.func has been overridden.

        UniqueMud:
            UniqueMud's func will:
                defer the action of the command.
                call Command.start_message if the command deffered successfully.
            If your command does not defer an action, override Command.func
            It is possible to use this method within your overidden one with:
                super().self.func()
        """
        caller = self.caller
        args = self.args
        caller_learning = caller.learning
        single_skill = args.replace('?', '') if args.endswith('?') else False
        # create a list of skills that have an increase available
        increaseable_skills = {}
        for skill_set_name, skill_names in skills.SKILLS.items():
            skill_set = getattr(caller.skills, skill_set_name, False)
            for skill_name in skill_names:
                if skill_name == 'skill_points':  # skip skill points attr
                    continue
                if caller_learning:  # skip skill currently being learned
                    if skill_name == caller_learning.get('skill_name'):
                        continue
                # get an instance of the command
                for set in caller.cmdset.get():
                    cmd_inst = set.get(skill_name)
                    if cmd_inst:
                        break
                exp_required = skills.rank_requirement(skill_set[skill_name]+1,
                                                       cmd_inst.learn_diff)
                # rank 0 commands require skill points to purchase
                if skill_set[skill_name] == 0:
                    increase_resource = skill_set['skill_points']
                else:
                    increase_resource = skill_set[skill_name+'_exp']
                # If the skill is ready for an increase, add it to the list
                if increase_resource >= exp_required:
                    increaseable_skills.update({skill_name: skill_set[skill_name]+1})
        if args:  # check if argument is ready for a rank increase
            if not caller.ready():  # stop the if that caller is not ready
                return False
            skill_name = single_skill if single_skill else args.lower()
            if skill_name in increaseable_skills:  # args is a skill ready for a rank increase
                if single_skill:
                    self.increaseable_ranks_msg({skill_name: increaseable_skills.get(skill_name)})
                    return True
                if caller_learning:
                    caller.msg(self.currently_learning_msg(''))
                    return True
                # defer the command
                defer_successful = self.defer()
                # message the caller and location
                if defer_successful:
                    learn_time = skills.learn_time(caller, skill_name)
                    stop_sugg = highlighter("stop", click_cmd=f"stop")
                    caller_msg = f'You begin to study {skill_name} to rank {increaseable_skills.get(skill_name)}.\n' \
                                 f'When you complete studing {skill_name}, it will take {timedelta(seconds=learn_time)} ' \
                                 'to learn the new rank.\nYou can not learn another skill during this time. ' \
                                 'You will be fully functional otherwise.\n' \
                                 'You can not stop learning after you have started. ' \
                                 'If you do not want learning to be locked out for this time use ' \
                                 f'{stop_sugg} before you have completed studing.'
                    caller.msg(caller_msg)
                    caller.emote_location(f'/Me begins to study {skill_name}.')
                    self.requires_ready = True  # Does the command require the ready status
            else:  # argument is not a skill with an increasable rank
                if caller_learning:
                    if not skill_name == caller_learning.get('skill_name'):
                        self.msg(f'{args}, is not an increasable skill.')
                else:
                    self.msg(f'{args}, is not an increasable skill.')
                self.increaseable_ranks_msg(increaseable_skills)
                return True
        else:  # no arguments show available rank increases
            self.increaseable_ranks_msg(increaseable_skills)
            return True

    def deferred_action(self):
        """
        This method is called after defer_time seconds when the Command.defer method is used.

        Usage:
            Intended to be overritten. Simply put the action portions of a command in this method.
        Returns:
            successful (bool): True if the command completed sucessfully.
                If this method returns True self.def_act_comp will be called after automatically.
        """
        # return the commnad to not requiring ready
        self.requires_ready = False  # Does the command require the ready status
        caller = self.caller
        skill_name = self.args.lower()
        rank = None
        # get the learn time
        learn_time = skills.learn_time(caller, skill_name)
        # create a persistent task
        task = delay(learn_time, skills.learn, caller.dbref, skill_name, persistent=True)
        # get the time learning will complete
        comp_date = time.time() + learn_time
        # get the rank this skill is upgrading to
        for skill_set_name, skill_names in skills.SKILLS.items():
            if skill_name in skill_names:
                skill_set = getattr(caller.skills, skill_set_name, False)
                rank = skill_set[skill_name] + 1
        if not rank:
            err_msg = f"Command learn, caller: {caller.id} | " \
                      f"failed to find skill {skill_name} in skills."
            error_report(err_msg, caller)
            return False
        caller.learning = {
                            'task_id': task.get_id(),
                            'comp_date': comp_date,
                            'skill_name': skill_name,
                            'rank': rank
                          }
        # message caller and location
        comp_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(caller.learning.get("comp_date")))
        msg = f'You complete studing {skill_name}, this rank increase will complete on {comp_date}.'
        caller.msg(msg)
        caller.emote_location(f'/Me completes studing {self.args.lower()}.')
        return True


class CmdStatus(Command):
    """
    Display information about your Character's statistics.

    Usage:
      stats, stat or statistics
    """
    key = "stat"
    aliases = ["statistics", "stats"]

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer
        self.requires_conscious = False  # if true this command requires the caller to be conscious

    def func(self):
        caller = self.caller
        # display name and appearance
        caller.msg("|/", force=True)
        caller.msg(f"Statistics for: |w{caller.name.capitalize()}|n", force=True)
        caller_msg = f"Others who do not know this Character see |o as: {caller.usdesc}"
        caller.msg(caller_msg, force=True)
        caller.msg("|/", force=True)
        # show health statistics
        caller.msg("Health:", force=True)
        row1 = list()
        row2 = list()
        for health_stat in ('hp', 'endurance'):
            row1.append(health_stat)
            if hasattr(caller, health_stat):
                health_value = getattr(caller, health_stat, 'Missing post check')
            else:
                health_value = 'Missing'
            row2.append('|w'+str(health_value)+'|n')
        health_list = [row1, row2]
        health_table = evtable.EvTable(table=health_list, border=None, pad_left=4)
        caller.msg(health_table, force=True)
        caller.msg("|/", force=True)
        # show attributes statistics
        caller.msg("Attributes:", force=True)
        row1 = list()
        row2 = list()
        row3 = list()
        row4 = list()
        # loop through statistics attributes
        for short_name, long_name in stats.STAT_MAP_DICT.items():
            # show two stats to a row
            if len(row1) < len(row3):
                first_row = row1
                second_row = row2
            else:
                first_row = row3
                second_row = row4
            # make the attribute clickable
            long_name = highlighter(long_name, click_cmd=f"help {long_name}", up=True)
            first_row.append(long_name)
            stat_value = getattr(caller, short_name, 'Missing')
            second_row.append("|w"+str(stat_value)+'|n')
        stats_list = [row1, row2, row3, row4]
        stats_table = evtable.EvTable(table=stats_list, border=None, pad_left=4)
        caller.msg(stats_table, force=True)
        caller.msg("|/", force=True)


class CmdCondition(Command):
    """
    Display information about your Character's condition.

    Usage:
      cond, condition
    """
    key = "condition"
    aliases = ["cond"]

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer
        self.requires_conscious = False  # if true this command requires the caller to be conscious

    def func(self):
        caller = self.caller
        # display name and appearance
        caller.msg("|/", force=True)
        caller.msg(f"Condition of: {caller.name}")
        row1 = list()
        row2 = list()
        row3 = list()
        row4 = list()
        # loop through statistics attributes
        for condition in CHARACTER_CONDITIONS:
            # show two stats to a row
            if len(row1) < len(row3):
                first_row = row1
                second_row = row2
            else:
                first_row = row3
                second_row = row4
            # make the attribute clickable
            condition = highlighter(condition, click_cmd=f"help {condition}", up=True)
            first_row.append(condition)
            state = 'No' if condition else 'Yes'
            second_row.append("|w"+str(state)+'|n')
        cond_list = [row1, row2, row3, row4]
        cond_table = evtable.EvTable(table=cond_list, border=None, pad_left=4)
        caller.msg(cond_table, force=True)
        caller.msg("|/", force=True)
        caller.msg(f"Position: {caller.position.capitalize()}", force=True)
        caller.msg("|/", force=True)
        caller.msg("Status:", force=True)
        status_table = evtable.EvTable(table=[], border_right_char='|', pad_left=4, pad_right=4)
        for status_type in ('busy', 'stunned'):
            status_name = highlighter(status_type.capitalize(), click_cmd=f"help {status_type}", up=True)
            if caller.nattributes.has(f'{status_type}_status'):
                status_list = []
                status_list.append(status_name)
                if caller.nattributes.has("deffered_command"):
                    cmd_name = caller.ndb.deffered_command.key.capitalize()
                    status_list.append(f"Action: {cmd_name}")
                    time_remain = status_delay_get(caller, status_type='busy')
                    time_remain = round(time_remain)
                    status_list.append(f"Time left: {time_remain}s")
                status_table.add_column(*status_list)
            else:
                status_table.add_column(status_name, "No")
        caller.msg(status_table, force=True)
        body_table = evtable.EvTable(table=[], pad_left=2, pad_right=2)
        body_list = []
        for part in caller.body.parts:
            part_inst = getattr(caller.body, part, False)
            for db_key, part_cond in part_inst.items():
                if part_cond:
                    # replace dbref with the instance of the object
                    if part_cond.startswith('#'):
                        part_cond = caller.search(part_cond).get_display_name(caller)
                    if body_list:
                        body_list.append(f"{db_key}: {part_cond}")
                    else:
                        body_list.append(part)
                        body_list.append(f"{db_key}: {part_cond}")
        if body_list:
            body_table.add_column(*body_list)
            caller.msg("Body:", force=True)
            caller.msg(body_table, force=True)


class CmdLook(EvCmdLook, Command):
    # Override look to use UM Command strucure.
    # Adds support for not working when the Character is unconscious.
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Status:
      look requires a Character be conscious

    Time:
      look takes no time to complete

    Observes your location or objects in your vicinity.
    """
    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        if self.args:  # a target was provided in command
            if not self.target:  # no target found
                caller.msg(f"You do not see {self.args} here.")
                return False
        else:  # no target was provided in command
            if not caller.location:  # caller has no location
                caller.msg("You have no location to look at!")
                err_msg = f"Command look, caller: {caller.id} | " \
                           "caller has no location."
                error_report(err_msg, caller)
                return False
            else:  # set the command's target to the caller's location
                self.target = caller.location
        return True  # custom requirements met, allow command to run

    def func(self):
        """
        Handle the looking.

        Obj.at_look, evennia.objects.objects.DefaultObject:
            Called when this object performs a look. It allows to
            customize just what this means. It will not itself
            send any data.

            Args:
                target (Object): The target being looked at. This is
                    commonly an object or the current location. It will
                    be checked for the "view" type access.
                **kwargs (dict): Arbitrary, optional arguments for users
                    overriding the call. This will be passed into
                    return_appearance, get_display_name and at_desc but is not used
                    by default.

            Returns:
                lookstring (str): A ready-processed look string
                    potentially ready to return to the looker.

        Obj.return_appearance in typeclasses.objects.Object
           called in the at_look method. Used to get proper rp names.
        """
        caller = self.caller
        target = self.target
        if not target:
            err_msg = f"Command look, caller: {caller.id} | " \
                       "caller has no location. After func call."
            error_report(err_msg, caller)
            return False
        # process the look
        self.msg((caller.at_look(target), {"type": "look"}), options=None)
        # if the character is looking at something other than the room.
        if not inherits_from(target, "typeclasses.rooms.Room"):
            if inherits_from(target, "typeclasses.exits.Exit"):
                if target.key in STANDARD_EXITS:  # if the target is a standard exit
                    room_msg = f"/Me looks /target."
                else:
                    room_msg = f"/Me looks through /target."
                caller.location.emote_contents(room_msg, caller, target, exclude=(caller,))
            else:
                if target is caller: # |o
                    room_msg = f"/Me looks at {caller.get_pronoun('|o')}self."
                    caller.location.emote_contents(room_msg, caller, exclude=(caller))
                else:
                    # target location is not caller or caller location
                    if target.location not in (caller, caller.location):
                        at_msg = f"something in /target"
                        em_targ = target.location
                    else:
                        at_msg = f"/target"
                        em_targ = target
                    room_msg = f"/Me looks at {at_msg}."
                    target_msg = f"/Me looks at you."
                    caller.location.emote_contents(room_msg, caller, em_targ, exclude=(caller, target))
                    target.emote(target_msg, sender=caller)


class CmdHelp(EvCmdHelp, Command):
    """
    View help or a list of topics

    Usage:
      help <topic or command>
      help list
      help all

    This will search for help on commands and other
    topics related to the game.
    """

    key = "help"
    aliases = ["?"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    # suggestion cutoff, between 0 and 1 (1 => perfect match)
    suggestion_cutoff = 0.6

    # number of suggestions (set to 0 to remove suggestions from help)
    suggestion_maxnum = 5

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer
        self.requires_conscious = False  # if true this command requires the caller to be conscious
        if not self.args:
            self.args = 'basic'

    def msg_help(self, text):
        """
        messages text to the caller, adding an extra oob argument to indicate
        that this is a help command result and could be rendered in a separate
        help window
        """
        if type(self).help_more:
            usemore = True

            if self.session and self.session.protocol_key in ("websocket", "ajax/comet"):
                try:
                    options = self.account.db._saved_webclient_options
                    if options and options["helppopup"]:
                        usemore = False
                except KeyError:
                    pass

            if usemore:
                evmore.msg(self.caller, text, session=self.session, force=True)
                return

        self.msg(text=(text, {"type": "help"}))

    def msg(self, text=None, to_obj=None, from_obj=None, session=None, **kwargs):
        """
        Overriding to allow option to show messages to dead and unconscious Characters
        """
        kwargs.update({"force": True})
        super().msg(text, to_obj, from_obj, session, **kwargs)


class CmdSay(Command):
    """
    speak as your character

    Usage:
      say <message>
      say to <target>, <target> "<message>"
          the first " is required when a target(s) is supplied.
          each target must have a , between the names.

    Example:
      say to blue droid, gray droid "Hello."

    Status
      say requires a Character to be conscious.

    Time
      say requires no time to complete

    Talk to those in your current location.
    """

    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"
    rhs_split = ('=', '"')

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer

    def func(self):
        """Run the say command"""
        caller = self.caller
        # if no speech stop command
        if not self.args:
            say_help = highlighter("help say", click_cmd="help say")
            help_msg = f"What would you like to say.|/Use {say_help}, for help."
            caller.msg(help_msg)
            return
        # if the command starts with string "to" or "at"
        if self.begins_to_or_at:
            if self.rhs:  # if message as a proper break in it
                if self.targets:  # if multiple targets were found
                    target = self.targets
                else:
                    target = self.target
                speech = self.rhs.strip('"')  # speech without quotes
                say_to_or_at = self.begins_to_or_at
                # message room
                room_message = f'/Me says {say_to_or_at} /target, "{speech}".'
                caller.location.emote_contents(room_message, caller, target, exclude=(caller,))
                # message the caller
                caller_message = f'You say {say_to_or_at} /target, "{speech}".'
                caller.emote(caller_message, target)
                return
        # No special targets, normal say
        speech = self.args
        # Calling the at_before_say hook on the character
        speech = caller.at_before_say(speech)
        if not speech:  # If speech is empty, stop here
            return
        # Call the at_after_say hook on the character
        caller.at_say(speech, msg_self=True)


class CmdWhisper(Command):
    """
    Speak privately as your character to another

    Usage:
      whisper <target> "<message>
      whisper to <target1>, <target2> "<message>"
          the first " is required.
          the " could also be =, to retain mux command support.
          each target must have a , between the names.

    Example:
      whisper to blue droid, gray droid "Hello."

    Status
      whisper requires a Character to be in the ready status.
        If you are whispering to someone it means your attention is focused there.

    Time
      whisper requires no time to complete
    """

    key = "whisper"
    locks = "cmd:all()"
    rhs_split = ('=', '"')

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player

    def func(self):
        """Run the whisper command"""
        caller = self.caller
        # if no speech stop command
        if not self.args:
            whisper_help = highlighter("help whisper", click_cmd="help whisper")
            help_msg = f"What would you like to whisper.|/" \
                       f"Use {whisper_help}, for help."
            caller.msg(help_msg)
            return
        if not self.rhs:
            whisper_help = highlighter("help whisper", click_cmd="help whisper")
            help_msg = f'The first " is required.|/' \
                       f'For example: whisper to door "Hello door."|/' \
                       f'Use {whisper_help}, for help.'
            caller.msg(help_msg)
            return
        if not self.begins_to_or_at:
            begins_to_or_at = 'to'
        else:
            begins_to_or_at = self.begins_to_or_at
        if self.targets:  # if multiple targets were found
            target = self.targets
            exclude = list(self.targets)
            exclude.append(caller)
        else:
            target = self.target
            exclude = [target, caller]
        speech = self.rhs.strip('"')  # speech without quotes
        whisper_to_or_at = begins_to_or_at
        # message room
        room_message = f'/Me whispers something {whisper_to_or_at} /target.'
        caller.location.emote_contents(room_message, caller, target=target, exclude=exclude)
        # message the caller
        caller_message = f'You whisper {whisper_to_or_at} /target, "{speech}".'
        caller.emote(caller_message, target)
        # message receivers
        receiver_message = f'/Me whispers {whisper_to_or_at} /target, "{speech}".'
        caller.emote(receiver_message, target, caller, target)


class CmdDrop(Command):
    """
    drop something

    Usage:
      drop <obj>

    Status:
      drop requires a Character to be conscious to use.

    Time:
      drop does not take any time to complete.

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.search_caller_only = True  # if True the command will only search the caller for targets
        self.requires_ready = False  # if true this command requires the ready status before it can do anything. deferal commands still require ready to defer

    def func(self):
        """Implement command"""
        caller = self.caller
        obj = self.target
        # shoot an error message if there is no target
        if not obj:
            error_report(f"Command drop, caller: {caller.id} | target not found, but func was still called.", caller)
            return
        # prevent dropping worn items that are covered by another worn item.
        elif obj.db.covered_by:
            caller.msg(f"You can't drop that because it's covered by {obj.db.covered_by}.")
            return
        # Inform player worn items must be removed to drop.
        elif obj.db.worn:
            obj_name = obj.get_display_name(caller)
            remove_help = highlighter(f"remove {obj_name}", click_cmd=f"remove {obj_name}")
            caller.msg(f"You must remove {obj_name} to drop it.\nTry command {remove_help} to remove it.")
            return
        obj.move_to(caller.location, quiet=True)  # move the object from the Character to the room
        # object being moved will remove itself from Character's hands in Object.at_after_move
        caller.emote("You drop /target.", target=obj)  # message the caller
        room_msg = "/Me drops /target."
        # message the room
        caller.location.emote_contents(room_msg, caller, obj, exclude=caller)
        obj.at_drop(caller)


class CmdGet(Command):
    """
    pick up something

    Usage:
      get <obj>

    status:
      get requires a Character to be in the ready status to use.

    Time:
      get, by default, requires 1 second to complete.
    """

    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        target = self.target
        # check if a hand is open
        open_hands = caller.open_hands()
        # hands are full, stop the command
        if not open_hands:
            stop_message = f"Your hands are full."
            caller.msg(stop_message)
            return False
        # stop the command if the caller is already caring the object.
        if target.location == caller:
            stop_message = f"You are already carrying /target."
            caller.emote(stop_message, target)
            return False
        return True  # custom requirements met, command can run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        if target.location == caller.location:  # get target is in caller's room
            caller_message = f"You reach for /target."
            caller.emote(caller_message, target)
            room_message = f"/Me reaches for /target."
            caller.location.emote_contents(room_message, caller, target, exclude=(caller,))
        else:  # get target is not in callers room
            caller_message = f"You reach into /target."
            caller.emote(caller_message, target.location)
            room_message = f"/Me reaches into /target."
            caller.location.emote_contents(room_message, caller, target.location, exclude=(caller,))

    def deferred_action(self):
        """implements the command."""

        caller = self.caller
        obj = self.target

        if not obj.access(caller, "get"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't get that.")
            return

        # calling at_before_get hook method
        if not obj.at_before_get(caller):
            return

        # check if a hand is open
        open_hands = caller.open_hands()
        # hands are full, stop the command
        # this repeat error checking is here itenetionally do not remove
        if not open_hands:
            caller.msg("Your hands are full.")
            return
        else:
            open_hand = open_hands[0]  # hand of the first open hand
        targ_old_location = obj.location  # used to choose message text
        success = obj.move_to(caller, quiet=True)
        if not success:
            caller.emote(f"/Target can not be picked up.", obj)
        else:
            # calling at_get hook method
            obj.at_get(caller)
            # occupy the hand used to get the object
            if open_hand:
                # occupy with dbref to make it very easy to search for items in hand
                open_hand.occupied = obj.dbref
            else:
                err_msg = f"CmdGet, failed for find an instance of the {open_hand} body part."
                error_report(err_msg, caller)
            # message player(s)
            if targ_old_location == caller.location:  # get target is in caller's room
                caller_msg = f"You pick up /target."
                location_msg = f"/Me picks up /target."
                caller.location.emote_contents(location_msg, caller, obj, exclude=caller)
            else:  # caller is getting target from container
                caller_msg = f"You get /target from {targ_old_location.usdesc}."
                location_msg = f"/Me gets /target from {targ_old_location.usdesc}."
            caller.emote(caller_msg, obj, caller)
            caller.location.emote_contents(location_msg, caller, obj, exclude=caller)


class CmdPut(Command):
    """
    Put an object in a container

    Usage:
      put <obj> in <container>

    Example:
      put book in bag

    status:
      put requires a Character to be in the ready status to use.

    Time:
      put, by default, requires 1 second to complete.
    """
    key = "put"
    aliases = "stow"
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    rhs_split = ('=', ' in ')

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command
        self.target_required = True  # if True and the command has no target, Command.func will stop execution and message the player
        self.can_not_target_self = True  # if True this command will end with a message if the Character targets themself
        self.target_in_hand = False  # if True the target of the command must be in the Characters hand to complete successfully
        self.requires_ready = True  # if true this command requires the ready status before it can do anything.

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        target = self.target
        if self.rhs:
            # Command.parse used rhs_split = ('=', ' in ') to collect the containers name in Command.rhs
            container_name = self.rhs.replace(" in ", '', 1)  # get the name of the container
            # find a reference of the container
            container = caller.search(container_name, quiet=True)
            if container:  # a possible container object was found
                container = container[0]  # get the correct target number
                # stop the command if the target can not move to the container
                if not target.at_before_move(container):
                    stop_message = "/Target is not a container."
                    caller.emote(stop_message, container)
                    return False  # Stop the command from running
                # target can be moved to container, notify caller and location
                self.container = container
                return True  # all custom requirements met, command can run
            else:  # no object of name container_name was found
                stop_message = f"You did not find {container_name} among your " \
                               "possesions or near by."
                caller.msg(stop_message)
                return False  # Stop the command from running
        else:
            cmd_help = highlighter('help put', click_cmd="help put", up=True)
            stop_message = "You must specify a container to place /target into.\n" \
                           f"For a full help use: {cmd_help}"
            caller.emote(stop_message, target)
            return False  # stop the command from running

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        target = self.target
        container = self.container  # collected in self.custom_requirements
        # message caller, making sender the container
        caller_message = "You begin to put /target into /me."
        caller.emote(caller_message, target, container)
        # message the room
        room_message = f"/Me begins to put /target into {container.usdesc}."
        caller.location.emote_contents(room_message, caller, target, exclude=(caller,))

    def deferred_action(self):
        caller = self.caller
        target = self.target
        container = self.container  # was collected in self.start_message
        if not target.at_before_get(container):
            return
        success = target.move_to(container, quiet=True)
        if success:
            target.at_get(container)
            # message the caller
            caller.emote("You put /target into /me.", target, container)
            # message the room
            room_msg = f"/Me puts /target into {container.usdesc}."
            caller.location.emote_contents(room_msg, caller, target, exclude=caller)
            # calling at_get hook method
            target.at_get(container)
        else:
            caller.emote("/Target can not be put into /me.", target, container)
            err_msg = f"CmdPut: caller: {caller.dbref}, target: {target.dbref} " \
                      f"container: {container.dbref}. target.move_to returned " \
                      f"false in Command.deferred_action."
            error_report(err_msg, caller)

class CmdInventory(Command):
    """
    view inventory

    Usage:
      inventory
      inv

    Status:
      inventory requires a Character to be in the ready status to use.

    Time:
      inventory, by default, takes 1 second to complete.

    Status and time requirements represent your Character searching through their belongings.

    Shows your inventory.
    """

    # Alternate version of the inventory command which separates
    # worn and carried items.

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        if not caller.contents:
            caller.msg("You are not carrying or wearing anything.")
            return False  # requirements not met stop the command
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        caller_pronoun = caller.get_pronoun('|a')
        message = "You rummage through your possessions, taking inventory."
        room_msg = f"/Me begings to quickly look through {caller_pronoun} possessions."
        caller.msg(message)
        caller.location.emote_contents(room_msg, caller, exclude=caller)

    def deferred_action(self):
        """check inventory"""
        caller = self.caller
        items = caller.contents

        carry_table = evtable.EvTable(border="header")
        wear_table = evtable.EvTable(border="header")
        for item in items:
            if not item.db.worn:
                carry_table.add_row("|C%s|n" % item.name, item.db.desc or "")
        if carry_table.nrows == 0:
            carry_table.add_row("|CNothing.|n", "")
        string = "|wYou are carrying:\n%s" % carry_table
        for item in items:
            if item.db.worn:
                wear_table.add_row("|C%s|n" % item.name, item.db.desc or "")
        if wear_table.nrows == 0:
            wear_table.add_row("|CNothing.|n", "")
        string += "|/|wYou are wearing:\n%s" % wear_table
        caller.msg(string)
        # Message the room
        caller_pronoun = caller.get_pronoun('|a')
        room_msg = f"/Me completes {caller_pronoun} search."
        caller.location.emote_contents(room_msg, caller, exclude=caller)


class CmdSit(Command):
    """
    sit down

    Usage:
      sit

    Status:
      sit requires a Character to be in the ready status to use.

    Time:
      sit, by default, takes 1 second to complete.

    Future support:
      add ability to sit on objects; chairs, tables, boxes so on.
    """

    key = "sit"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        if caller.position == 'sitting':
            caller.msg("You are already sitting.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        caller.msg("You move to sit down.")
        caller.emote_location("/Me moves to sit down.")

    def deferred_action(self):
        """Implement command"""
        caller = self.caller
        success = caller.sit()
        if success:
            caller.msg("You sit down.")
            caller.emote_location("/Me sits down.")


class CmdStand(Command):
    """
    stand up

    Usage:
      stand

    Status:
      stand requires a Character to be in the ready status to use.

    Time:
      stand, by default, takes 3 seconds to complete.
    """

    key = "stand"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        if caller.position == 'standing':
            caller.msg("You are already standing.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        caller.msg("You move to stand up.")
        caller.emote_location("/Me moves to stand up.")

    def deferred_action(self):
        """Implement command"""
        caller = self.caller
        success = caller.stand()
        if success:
            caller.msg("You stand up.")
            caller.emote_location("/Me stands up.")


class CmdLay(Command):
    """
    lay down

    Usage:
      lay

    Status:
      lay requires a Character to be in the ready status to use.

    Time:
      lay, by default, takes 1 second to complete.
    """

    key = "lay"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def set_instance_attributes(self):
        """Called automatically at the start of at_pre_cmd.

        Here to easily set command instance attributes.
        """
        self.defer_time = 1  # time is seconds for the command to wait before running action of command

    def custom_requirements(self):
        """Verifies commands custom requirements are met. If this method returns False the command will end.
        This method must message the caller why the command failed.

        This command is called automatically in at_pre_cmd and again just before deferred_action.
        self.target and self.targets will be available in this method.

        This method is intended to be overwritten.

        Returns:
            requirements_met (bool): If True the command continues. If Falsey the command ends.

        """
        caller = self.caller
        if caller.position == 'laying':
            caller.msg("You are already laying.")
            return False
        return True  # custom requirements met, allow command to run

    def start_message(self):
        """
        Display a message after a command has been successfully deffered.

        Automatically called at the end of Command.func
        """
        caller = self.caller
        caller.msg("You move to lay down")
        caller.emote_location("/Me moves to lay down.")

    def deferred_action(self):
        """Implement command"""
        caller = self.caller
        success = caller.lay()
        if success:
            caller.msg("You lay down.")
            caller.emote_location("/Me lays down.")


class UMRPSystemCmdSet(CmdSet):
    """
    Overridden RP system's commands.

    Reason:
        deny access to commands sdesc, pose and mask to those without builder permision
    """

    def at_cmdset_creation(self):
        self.add(CmdEmote)
        self.add(CmdRecog)
        self.add(CmdSdesc)
        self.add(CmdPose)
        self.add(CmdMask)


class CmdPose(rpsystem.CmdPose):
    # rpsystem overriden CmdPose
    locks = "perm(Builder)"
    help_category = "Building"


class CmdSdesc(rpsystem.CmdSdesc):
    # rpsystem overriden CmdSdesc
    locks = "perm(Builder)"
    help_category = "Building"


class CmdMask(rpsystem.CmdMask):
    # rpsystem overriden CmdMask
    locks = "perm(Builder)"
    help_category = "Building"


class CmdRecog(rpsystem.CmdRecog, Command):
    pass


class CmdEmote(rpsystem.CmdEmote, Command):
    pass
