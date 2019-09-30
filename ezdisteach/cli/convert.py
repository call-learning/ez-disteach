import argparse
import os

import olag.filters.input
import olag.filters.output


def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


outputfilterpluginslist = olag.filters.output.get_output_filter_plugins()

parser = argparse.ArgumentParser(description='Convert EZ-DisTeach project into a Course')

parser.add_argument('pathin',
                    type=is_dir,
                    help='Path from which we fetch the files')

parser.add_argument('pathout',
                    type=argparse.FileType('wb'),
                    help='Zip file path to which we produce the output')

parser.add_argument('--out-format',
                    metavar='outputformat',
                    choices=[plugin.__name__.lower() for plugin in outputfilterpluginslist],
                    default='imscontentpackageoutput',
                    help='Output format')

args = parser.parse_args()


