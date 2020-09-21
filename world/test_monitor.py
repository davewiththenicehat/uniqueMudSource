"""
Used to test the monitor handler module
"""


def monitor_callback(fieldname="", obj=None, **kwargs):
    # reporting callback that works both
    # for db-fields and Attributes
    obj.msg("Checking for HP Changed.")
    if fieldname.startswith("db_"):
        new_value = getattr(obj, fieldname)
    else:  # an attribute
        new_value = obj.attributes.get(fieldname)

    obj.msg("%s.%s changed to '%s'." % (obj.key, fieldname, new_value))

# (we could add _some_other_monitor_callback here too)

# monitor Attribute (assume we have obj from before)
# monitorhandler.add(obj, "desc", _monitor_callback)

# monitor same db-field with two different callbacks (must separate by id_string)
# monitorhandler.add(obj, "db_key", _monitor_callback, id_string="foo")
# monitorhandler.add(obj, "db_key", _some_other_monitor_callback, id_string="bar")
