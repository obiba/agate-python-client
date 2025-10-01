#
# Agate commands main entry point
#
import argparse
import getpass
import sys

import obiba_agate.rest as rest
import obiba_agate.auth_management.application as application
import obiba_agate.auth_management.group as group
import obiba_agate.auth_management.user as user

def prompt_password():
    return getpass.getpass(prompt='Enter password:')

def add_agate_arguments(parser):
    """
    Add Agate access arguments
    """
    parser.add_argument('--agate', '-ag', required=False, default='http://localhost:8081',
                        help='Agate server base url (default: http://localhost:8081)')
    parser.add_argument('--user', '-u', required=False, help='User name')
    parser.add_argument('--password', '-p', nargs="?", required=False, help='User password')
    parser.add_argument('--otp', '-ot', action='store_true', help='Whether a one-time password is to be provided (required when connecting with username/password AND two-factor authentication is enabled)')
    parser.add_argument('--ssl-cert', '-sc', required=False, help='Certificate (public key) file')
    parser.add_argument('--ssl-key', '-sk', required=False, help='Private key file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-ssl-verify', '-nv', action='store_true', help='Do not verify SSL certificates for HTTPS.')


def add_subcommand(subparsers, name, help, add_args_func, default_func):
    """
    Make a sub-parser, add default arguments to it, add sub-command arguments and set the sub-command callback function.
    """
    subparser = subparsers.add_parser(name, help=help)
    add_agate_arguments(subparser)
    add_args_func(subparser)
    subparser.set_defaults(func=default_func)


def run():
    """
    Command-line entry point.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Agate command line.')
    subparsers = parser.add_subparsers(title='sub-commands',
                                      help='Available sub-commands. Use --help option on the sub-command '
                                            'for more details.')

    # Add subcommands
    add_subcommand(subparsers, 'rest', 'Request directly the Agate REST API, for advanced users.', rest.add_arguments,
                  rest.do_command)
    add_subcommand(subparsers, 'add-user', 'Add a new user.',
                  user.user_add_arguments, user.do_add_command)
    add_subcommand(subparsers, 'delete-user', 'Delete a user.',
                  user.user_delete_arguments,
                  user.do_delete_command)
    add_subcommand(subparsers, 'add-group', 'Add a new group.',
                  group.group_add_arguments,
                  group.do_add_command)
    add_subcommand(subparsers, 'delete-group', 'Delete a group (does NOT delete users of the group).',
                  group.group_delete_arguments,
                  group.do_delete_command)
    add_subcommand(subparsers, 'add-application', 'Add a new application.',
                  application.application_add_arguments,
                  application.do_add_command)
    add_subcommand(subparsers, 'delete-application',
                  'Delete an application.',
                  application.application_delete_arguments,
                  application.do_delete_command)

    # Execute selected command
    args = parser.parse_args()

    try:
        if not args.password or len(args.password) == 0:
            args.password = prompt_password()
            pass
    except AttributeError:
        args.password = prompt_password()

    if hasattr(args, 'func'):
        try:
            args.func(args)
        except Exception as e:
            print(e)
            sys.exit(2)
    else:
      print('Agate command line tool.')
      print('For more details: agate --help')
