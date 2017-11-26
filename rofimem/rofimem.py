from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import contextlib

import os
import subprocess
import threading
import json
import fasteners


def read_json(filename):
    if os.path.exists(filename):
        with open(filename) as stream:
            return json.loads(stream.read())
    else:
        return dict()

DEFAULT_DATA_DIR = os.path.join(os.environ['HOME'], '.config', 'rofimem')

PARSER = argparse.ArgumentParser(description='')
PARSER.add_argument(
    '--config-dir', '-D', type=str,
    default=DEFAULT_DATA_DIR,
    help='configuration file')
PARSER.add_argument(
    'name', type=str, default='default', nargs='?',
    help='Set of options to use')
PARSER.add_argument(
    '--history', action='store_true', default=False,
    help='Select from history')

args = PARSER.parse_args()


DATA_LOCK = threading.Lock()
@contextlib.contextmanager
def with_data(data_file):
    "Read from a json file, write back to it when we are finished"
    with fasteners.InterProcessLock(data_file + '.lck'):
        with DATA_LOCK:
            data = read_json(data_file)
            yield data

            output = json.dumps(data)
            with open(data_file, 'w') as stream:
                stream.write(output)

def rofi_prompt(prompt, choices):
    p = subprocess.Popen(
        [b'rofi', b'-dmenu', b'-p', prompt.encode('utf8')],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    choice_string = b'\n'.join([c.encode('utf8') for c in choices])
    reply, _ = p.communicate(choice_string)
    return reply.decode('utf8').strip()

def zenity_read(prompt, initial=''):
    return subprocess.check_output([
        'zenity', '--entry', '--text',
        prompt, '--entry-text', initial]).decode('utf8')

def main():
    with with_data(os.path.join(args.config_dir, 'data.json')) as data:
        while True:
            data.setdefault('options', dict())
            data.setdefault('history', dict())
            if args.name not in data['options']:
                data['options'][args.name] = []

            if args.name not in data['history']:
                data['history'][args.name] = []

            options = data['options'][args.name]
            history = data['history'][args.name]

            if args.history:
                result = rofi_prompt('Input:', reversed(history))
            else:
                result = rofi_prompt('Input:', ['* new', '* edit', '* delete', '* history'] + options)

            if result == '* history':
                result = rofi_prompt('Input (Control-enter for input):', reversed(history))
            if result == '* new':
                new_entry = rofi_prompt('New entry:', history)
                options.append(new_entry.strip('\n'))
            elif result == '* edit':
                edit = rofi_prompt('Item to edit', options)
                new_entry = zenity_read('New entry:', edit)
                options.remove(edit)
                options.append(new_entry.strip('\n'))
            elif result == '* delete':
                removed = rofi_prompt('Item to edit', options)
                options.remove(removed)
            else:
                while result in history:
                    history.remove(result)
                history.append(result)
                print(result)
                break
