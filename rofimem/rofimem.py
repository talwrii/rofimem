from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import contextlib
# make code as python 3 compatible as possible

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
PARSER.add_argument('--config-dir', '-D', type=str, help='configuration file', default=DEFAULT_DATA_DIR)
PARSER.add_argument('name', type=str, help='Set of options to use', default='default', nargs='?')
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
            if args.name not in data['options']:
                data['options'][args.name] = []

            options = data['options'][args.name]

            result = rofi_prompt('Input:', options + ['* new', '* edit', '* delete'])
            if result == '* new':
                new_entry = rofi_prompt('New entry:', [])
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
                print(result)
                break
