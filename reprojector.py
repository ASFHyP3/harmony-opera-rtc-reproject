"""
==================
example_service.py
==================

An example service adapter implementation and example CLI parser
"""

import argparse
import shutil
import os
from pathlib import Path
from tempfile import mkdtemp

import asf_search
from osgeo import gdal

import harmony
from harmony.util import stage

class ExampleAdapter(harmony.BaseHarmonyAdapter):
    """
    Shows an example of what a service adapter implementation looks like
    """
    def process_item(self, granules: list, output_srs: str):

        workdir = mkdtemp()
        session = asf_search.ASFSession()
        results = asf_search.granule_search(granules)

        aws_urls = []

        for index in len(results):
            try:
                print(f'Processing granule {granule}')

                # Download the relevant files for the product.
                granule = granules[index]
                results[index].download(path='.', session=session, fileType=asf_search.download_file_type.FileDownloadType.ADDITIONAL_FILES)
                input_files = [granule + '_VV.tif', granule + '_VH.tif', granule + '_mask.tif']
                output_files = list(map(lambda f: str(Path(workdir) / (f.split('.tif')[0] + '_reprojected.tif')), input_files))

                # Do the reprojection for each file.
                for file_index in len(input_files):
                    gdal.Translate(output_files[file_index], input_files[file_index], format='COG', creationOptions=['NUM_THREADS=all_cpus'], dstSRS=output_srs)
                    url = stage(output_files[file_index], output_files[file_index], 'image/geotiff', location=self.message.stagingLocation,
                            logger=self.logger)
                    aws_urls.append(url)

                return aws_urls
            finally:
                # Clean up any intermediate resources
                shutil.rmtree(workdir)


def run_cli(args):
    """
    Runs the CLI.  Presently stubbed to demonstrate how a non-Harmony CLI fits in and allow
    future implementation or removal if desired.

    Parameters
    ----------
    args : Namespace
        Argument values parsed from the command line, presumably via ArgumentParser.parse_args

    Returns
    -------
    None
    """
    print("TODO: You can implement a non-Harmony CLI here.")
    print('To see the Harmony CLI, pass `--harmony-action=invoke '
          '--harmony-input="$(cat example/example_message.json)" '
          '--harmony-sources=example/source/catalog.json --harmony-output-dir=tmp/`')



def main():
    """
    Parses command line arguments and invokes the appropriate method to respond to them

    Returns
    -------
    None
    """
    parser = argparse.ArgumentParser(prog='example', description='Run an example service')

    harmony.setup_cli(parser)

    args = parser.parse_args()

    if (harmony.is_harmony_cli(args)):
        harmony.run_cli(parser, args, ExampleAdapter)
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
