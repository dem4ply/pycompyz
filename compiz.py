#!/usr/bin/env python

import sys, dbus, subprocess

METHOD_ACTIVATE, METHOD_LIST = range(2)

booldict = {'true': True, 'false': False}


def destrify(s):
    '''Attempt to turn a string into an int, float, or bool'''

    value = None
    try:
        i = int(s, 0)
    except ValueError:
        try:
            f = float(s)
        except ValueError:
            value = booldict.get(s.lower(), s)
        else:
            value = f
    else:
        value = i

    return value

'''Function to call any Compiz method.  I am sorry for
the real hackishness nature of this module, but I just
need it to work, and I need it to work now.  In a future
moment I might spin it off into PyCompiz or something, 
and rewrite most of it.  For now though, it does work.
'''
def call(*argv):
	argv = list(argv)
	argv.insert(0, '') #So we don't have to restructure code
	# Getting root window ID
	try:
	    rootwin = subprocess.Popen(['xwininfo', '-root'],
		stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

	except OSError:
	    raise SystemExit('Error: xwininfo not present')

	try:
	    rootwin_id = int(rootwin.split()[3], 0)

	except IndexError:
	    raise SystemExit('Error: unexpectedly short output from xwininfo')

	except ValueError:
	    raise SystemExit('Error: unable to convert "%s" to int', rootwin.split()[3])


	# Argument parsing

	if len(argv) < 3:
	    if len(argv) == 2:
		method = METHOD_LIST
	    else:
		raise SystemExit('Error: too few arguments')
	else:
	    method = METHOD_ACTIVATE

	plugin = argv[1]
	if method == METHOD_ACTIVATE:
	    action = argv[2]

	args = ['root', rootwin_id]

	extra_len = len(argv[3:])
	if extra_len >= 2 and extra_len % 2 == 0:
	    for k, v in zip(argv[3::2], argv[4::2]):
		args.append(k)
		args.append(destrify(v))


	# D-Bus call

	service = interface = 'org.freedesktop.compiz'

	session_bus = dbus.SessionBus()

	if method == METHOD_ACTIVATE:
	    proxy = session_bus.get_object(service,
		'/org/freedesktop/compiz/%s/allscreens/%s' %(plugin, action))
	    obj = dbus.Interface(proxy, interface)
	    obj.activate(*args)

	elif method == METHOD_LIST:
	    proxy = session_bus.get_object(service,
		'/org/freedesktop/compiz/%s/allscreens' %(plugin))
	    obj = dbus.Interface(proxy, interface)
	    print '\n'.join(obj.list())
