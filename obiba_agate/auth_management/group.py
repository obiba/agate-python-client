"""
Python commands for adding or deleting a Group
"""

import json
import obiba_agate.core as core


def group_add_arguments(parser):
    """
    Add agate group management arguments
    """

    parser.add_argument('--name', help='The group Name (required), it must be unique', required=True)
    parser.add_argument('--description', help='The group Description', required=False)
    parser.add_argument('--applications',
                        help='Members of a group get access to the applications associated to this group',
                        required=False, nargs='*')


def do_add_command(args):
    """
    Execute add group management command
    """

    request = core.AgateClient.build(core.AgateClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()

    if args.verbose:
        request.verbose()

    group = {'name': args.name}
    if args.description:
        group['description'] = args.description
    if args.applications:
        group['applications'] = args.applications

    request.post().content_type_json().resource(core.UriBuilder(['groups']).build()).content(
        json.dumps(group))

    response = request.send()
    print(response.content)

def group_delete_arguments(parser):
    """
    Add agate group management arguments
    """

    parser.add_argument('--name', help='The group Name (required)', required=True)


def do_delete_command(args):
    """
    Execute delete group management command
    """

    request = core.AgateClient.build(core.AgateClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()

    request.delete().content_type_json().resource(core.UriBuilder(['group', args.name]).build())

    response = request.send()
    print(response.content)
