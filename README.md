# Agate Python [![CI](https://github.com/obiba/agate-python-client/actions/workflows/ci.yml/badge.svg)](https://github.com/obiba/agate-python-client/actions/workflows/ci.yml)

This Python-based command line tool allows to access to a Agate server through its REST API. This is the perfect tool
for automating tasks in Agate. This will be the preferred client developed when new features are added to the REST API.

* Read the [documentation](http://agatedoc.obiba.org).
* Have a bug or a question? Please create a [GitHub issue](https://github.com/obiba/agate-python-client/issues).
* Continuous integration is on [GitHub actions](https://github.com/obiba/agate-python-client/actions).

## Usage

Install with:

```
pip install obiba-agate
```

To get the options of the command line:

```
agate --help
```

This command will display which sub-commands are available. For each sub-command you can get the help message as well:

```
agate <subcommand> --help
```

The objective of having sub-command is to hide the complexity of applying some use cases to the Agate REST API. More
sub-commands will be developed in the future.

## Development

Agate Python client can be easily extended by using the classes defined in `core.py` and in `protobuf/*.py` files.

## Mailing list

Have a question? Ask on our mailing list!

obiba-users@googlegroups.com

[http://groups.google.com/group/obiba-users](http://groups.google.com/group/obiba-users)

## License

OBiBa software are open source and made available under the [GPL3 licence](http://www.obiba.org/pages/license/). OBiBa software are free of charge.

## OBiBa acknowledgments

If you are using OBiBa software, please cite our work in your code, websites, publications or reports.

"The work presented herein was made possible using the OBiBa suite (www.obiba.org), a  software suite developed by Maelstrom Research (www.maelstrom-research.org)"
