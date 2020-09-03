from evennia import create_object, search_object
from typeclasses import rooms, exits
from evennia.utils import evtable
from world import map_module

# We begin by creating our rooms so we can detail them later.

centre = create_object(rooms.Room, key="crossroads")
north = create_object(rooms.Room, key="castle")
east = create_object(rooms.Room, key="cottage")
south = create_object(rooms.Room, key="camp")
west = create_object(rooms.Room, key="coast")

# This is where we set up the cross roads.
# The rooms description is what we see with the 'look' command.

# The cross roads.
# We pass what we want in our table and EvTable does the rest.
# Passing two arguments will create two columns but we could add more.
# We also specify no border.
centre.db.desc = evtable.EvTable(map_module.return_minimap(4,5),
                 "The merger of two roads. A single lamp post dimly " \
                 "illuminates the lonely crossroads. To the north " \
                 "looms a mighty castle. To the south the glow of " \
                 "a campfire can be seen. To the east lie a wall of " \
                 "mountains and to the west the dull roar of the open sea.",
                 border=None)
# EvTable allows formatting individual columns and cells. We use that here
# to set a maximum width for our description, but letting the map fill
# whatever space it needs.
centre.db.desc.reformat_column(1, width=70)

# Here we are creating exits from the centre "crossroads" location to
# destinations to the north, east, south, and west. We will be able
# to use the exit by typing it's key e.g. "north" or an alias e.g. "n".

centre_north = create_object(exits.Exit, key="north",
                            aliases=["n"], location=centre, destination=north)
centre_east = create_object(exits.Exit, key="east",
                            aliases=["e"], location=centre, destination=east)
centre_south = create_object(exits.Exit, key="south",
                            aliases=["s"], location=centre, destination=south)
centre_west = create_object(exits.Exit, key="west",
                            aliases=["w"], location=centre, destination=west)

# Now we repeat this for the other rooms we'll be implementing.
# This is where we set up the northern castle.

# The northern castle.
north.db.desc = evtable.EvTable(map_module.return_minimap(4,2),
                "An impressive castle surrounds you. There might be " \
                "a princess in one of these towers.",
                border=None)
north.db.desc.reformat_column(1, width=70)
north_south = create_object(exits.Exit, key="south",
                            aliases=["s"], location=north, destination=centre)

# This is where we set up the eastern cottage.

# The eastern cottage.
east.db.desc = evtable.EvTable(map_module.return_minimap(6,5),
               "A cosy cottage nestled among mountains stretching " \
               "east as far as the eye can see.",
               border=None)
east.db.desc.reformat_column(1, width=70)
east_west = create_object(exits.Exit, key="west",
                            aliases=["w"], location=east, destination=centre)

# This is where we set up the southern camp.

# The southern camp.
south.db.desc = evtable.EvTable(map_module.return_minimap(4,7),
                "Surrounding a clearing are a number of tribal tents " \
                "and at their centre a roaring fire.",
                border=None)
south.db.desc.reformat_column(1, width=70)
south_north = create_object(exits.Exit, key="north",
                            aliases=["n"], location=south, destination=centre)

# This is where we set up the western coast.

# The western coast.
west.db.desc = evtable.EvTable(map_module.return_minimap(2,5),
               "The dark forest halts to a sandy beach. The sound of " \
               "crashing waves calms the soul.",
               border=None)
west.db.desc.reformat_column(1, width=70)
west_east = create_object(exits.Exit, key="east",
                            aliases=["e"], location=west, destination=centre)

# Lastly, lets make an entrance to our world from the default Limbo room.

limbo = search_object('Limbo')[0]
limbo_exit = create_object(exits.Exit, key="enter world",
                            aliases=["enter"], location=limbo, destination=centre)

"""
Created following:
https://github.com/evennia/evennia/wiki/Static-In-Game-Map
"""
