import argparse
import os


class WriteableDir(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError(f"writable_dir: {prospective_dir} is not a valid path")
        if os.access(prospective_dir, os.W_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError(f"writable_dir: {prospective_dir} is not a writable dir")
