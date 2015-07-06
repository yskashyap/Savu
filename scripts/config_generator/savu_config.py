'''
Created on 21 May 2015

@author: ssg37927
'''

import os

from savu.data.process_data import ProcessList
from savu.plugins import utils as pu
import pkgutil
import savu


class Content(object):

    def __init__(self, filename):
        self.process_list = ProcessList()
        if os.path.exists(filename):
            print "Opening file %s" % (filename)
            self.process_list.populate_process_list(filename)

    def display(self):
        print self.process_list.get_string()

    def save(self, filename):
        self.process_list.save_list_to_file(filename)

    def modify(self, element, subelement, value):
        data_elements = self.process_list.process_list[element-1]['data']
        if subelement in data_elements.keys():
            data_elements[subelement] = value
        else:
            print("Sorry, element %i does not have a %s parameter" %
                  (element, subelement))

    def insert(self, plugin, pos):
        process = {}
        process['name'] = plugin.name
        process['id'] = "savu.plugins." + plugin.__module__
        process['data'] = plugin.parameters
        self.process_list.process_list.insert(pos, process)

    def remove(self, pos):
        self.process_list.process_list.pop(pos)


def _help(content, arg):
    """Display the help information"""
    for key in commands.keys():
        print "%4s : %s" % (key, commands[key].__doc__)
    return content


def _open(content, arg):
    """Opens or creates a new configuration file with the given filename"""
    ct = Content(arg)
    ct.display()
    return ct


def _disp(content, arg):
    """Displays the process in the current list"""
    content.display()
    return content


def _list(content, arg):
    """List the plugins which have been registered for use"""
    for key in pu.plugins.keys():
        print(key)
        plugin = pu.plugins[key]()
        plugin.populate_default_parameters()
        for p_key in plugin.parameters.keys():
            print("    %20s : %s" % (p_key, plugin.parameters[p_key]))
    return content


def _save(content, arg):
    """Save the current list to disk with the filename given"""
    content.save(arg)
    return content


def _mod(content, arg):
    """Modifies the target value e.g. 'mod 1.value 27'"""
    try:
        element,  subelement = arg.split()[0].split('.')
        value = None
        exec("value = " + arg.split()[1])
        content.modify(int(element), subelement, value)
        content.display()
    except:
        print("Sorry i can't process the argument '%s'" % (arg))
    return content


def _add(content, arg):
    """Adds the named plugin before the specified location 'MedianFilter 2'"""
    try:
        name, pos = arg.split()
        if name in pu.plugins.keys():
            plugin = pu.plugins[name]()
            plugin.populate_default_parameters()
            content.insert(plugin, int(pos)-1)
            content.display()
        else:
            print("Sorry the plugin %s is not in my list, pick one form list" %
                  (name))
    except:
        print("Sorry i can't process the argument '%s'" % (arg))
    return content


def _rem(content, arg):
    """Remove the numbered item from the list"""
    content.remove(int(arg)-1)
    content.display()
    return content

commands = {'open': _open,
            'help': _help,
            'disp': _disp,
            'list': _list,
            'save': _save,
            'mod': _mod,
            'add': _add,
            'rem': _rem}

if __name__ == '__main__':
    print "Starting Savu Config tool"

    # load all the packages in the plugins directory to register classes
    for loader, module_name, is_pkg in pkgutil.walk_packages(savu.plugins.__path__):
        try:
            module = loader.find_module(module_name).load_module(module_name)
        except:
            pass

    # set up things
    input_string = "startup"
    content = Content("")

    while True:
        input_string = raw_input(">>> ").strip()
        print "command is '%s'" % (input_string)

        command = input_string.split()[0]
        arg = ' '.join(input_string.split()[1:])

        if 'exit' in command:
            break

        # try to run the command
        if command in commands.keys():
            content = commands[command](content, arg)
        else:
            print "I'm sorry, thats not a command I recognise, try help"

    print "Thanks for using the application"
