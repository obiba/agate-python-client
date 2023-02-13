"""
Python commands for adding or deleting an Application
"""

import json
import obiba_agate.core as core


def application_add_arguments(parser):
    """
    Add agate application management arguments
    """

    parser.add_argument('--name', help='The application Name (required), it must be unique', required=True)
    parser.add_argument('--description', help='The application description', required=False)
    parser.add_argument('--key', help='The application Key (required)', required=True)
    parser.add_argument('--redirect', help='Callback URL to the application\'s server, required in the OAuth context',
                        required=False)
    parser.add_argument('--manual-approval', help='User signing up through the application is in "pending for approval" state', required=False)


def do_add_command(args):
    """
    Execute add application management command
    """

    request = core.AgateClient.build(core.AgateClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()

    if args.verbose:
        request.verbose()

    application = {'name': args.name, 'key': args.key}
    if args.description:
        application['description'] = args.description
    if args.redirect:
        application['redirectURI'] = args.redirect
    if args.manual_approval:
        application['autoApproval'] = False

    request.post().content_type_json().resource(core.UriBuilder(['applications']).build()).content(
        json.dumps(application))

    response = request.send()
    print(response.content)


def application_delete_arguments(parser):
    """
    Add agate application management arguments
    """

    parser.add_argument('--name', help='The application Name (required)', required=True)


def do_delete_command(args):
    """
    Execute delete application management command
    """

    request = core.AgateClient.build(core.AgateClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()

    request.delete().content_type_json().resource(core.UriBuilder(['application', args.name]).build())

    response = request.send()
    print(response.content)
