from evennia import DefaultObject, search_object
from typeclasses.trainscript import TrainStoppedScript
from commands.train import CmdSetTrain

class TrainObject(DefaultObject):

    def at_object_creation(self):
        self.cmdset.add_default(CmdSetTrain)
        self.db.driving = False
        # The direction our train is driving (1 for forward, -1 for backwards)
        self.db.direction = 1
        # The rooms our train will pass through (change to fit your game)
        self.db.rooms = ["#178", "#181", "#184", "#187"]
        self.scripts.add(TrainStoppedScript)

    def start_driving(self):
        self.db.driving = True

    def stop_driving(self):
        self.db.driving = False

    def goto_next_room(self):
        currentroom = self.location.dbref
        idx = self.db.rooms.index(currentroom) + self.db.direction

        if idx < 0 or idx >= len(self.db.rooms):
            # We reached the end of our path
            self.stop_driving()
            # Reverse the direction of the train
            self.db.direction *= -1
        else:
            roomref = self.db.rooms[idx]
            room = search_object(roomref)[0]
            self.move_to(room)
            self.msg_contents("The train is moving forward to %s." % (room.name, ))
