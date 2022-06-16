#!/bin/python3

import argparse
import sys
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union, Optional, Tuple

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Patch, Ellipse, Rectangle, Circle

SUPPORTED_FILE_TYPES = tuple(plt.gcf().canvas.get_supported_filetypes().keys())


class AbstractPlotter(ABC):
    @abstractmethod
    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            output_type: str = 'show',
            output_file_path: Optional[Path] = None
    ):
        self.plotted_data: Union[Patch, None] = None
        self.coordinates: Tuple[float, float] = (x, y)
        self.output_type: str = output_type
        self.output_file_path: Union[Path, None] = output_file_path.absolute() if output_file_path else None

    @classmethod
    def run(cls, *args, **kwargs):
        plotter = cls(*args, **kwargs)
        plotter.plot()
        plotter.do_output()

    def do_output(self):
        assert self.plotted_data

        if self.output_type == 'console':
            matplotlib.use('module://drawilleplot')

        ax = plt.gca()
        ax.set_axis_off()
        ax.add_patch(self.plotted_data)
        plt.axis("scaled")

        if self.output_type in ('show', 'console'):
            plt.show()
        elif self.output_type == 'file':
            plt.savefig(self.output_file_path)

    @abstractmethod
    def plot(self):
        pass


class CirclePlotter(AbstractPlotter):
    def __init__(self, *args, radius: float, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius: float = radius

    def plot(self):
        circle = Circle(self.coordinates, self.radius)

        self.plotted_data = circle


class RectanglePlotter(AbstractPlotter):
    def __init__(self, *args, width: float, height: float, angle: float, **kwargs):
        super().__init__(*args, **kwargs)
        self.width: float = width
        self.height: float = height
        self.angle: float = angle

    def plot(self):
        rectangle = Rectangle(self.coordinates, self.width, self.height, angle=self.angle)

        self.plotted_data = rectangle


class EllipsePlotter(RectanglePlotter):
    def plot(self):
        rectangle = Ellipse(self.coordinates, self.width, self.height, angle=self.angle)

        self.plotted_data = rectangle


class ArgsParser:
    def __init__(self):
        self.script_args = None

        self.parser = argparse.ArgumentParser(
            description='Script that plots geometric figures\n'
                        f'Try {sys.argv[0]} {{figuretype}} -h '  # NOQA
                        f'to get help for specific figure plotting arguments\n'
                        f'If output type is file, output file path must be with one of supported extensions\n'
                        f'Supported output formats: {", ".join(("show", "console", *SUPPORTED_FILE_TYPES))}',
            formatter_class=argparse.RawTextHelpFormatter
        )
    
        self.parser.add_argument('-t',
                                 '--outputtype',  # NOQA
                                 help=f'Output type. If choice is file, -o must be specified',
                                 required=True,
                                 choices=('file', 'show', 'console'))

        self.parser.add_argument('-o',
                                 '--outputfile',  # NOQA
                                 help='Path to output file (if output type is file)',
                                 required=False,
                                 type=Path)

        self.parser.add_argument('-x',
                                 help='X Coordinate where to plot',
                                 required=False,
                                 default=0,
                                 type=float)

        self.parser.add_argument('-y',
                                 help='Y Coordinate where to plot',
                                 required=False,
                                 default=0,
                                 type=float)
    
        figure_subparser = self.parser.add_subparsers(
            dest='figuretype',   # NOQA
            description='Figure type to plot',
            required=True,
        )
    
        circle_parser = figure_subparser.add_parser('circle')
        circle_parser.add_argument('radius', type=float, help='Radius of circle to plot')
    
        rectangle_parser = figure_subparser.add_parser('rectangle')
        rectangle_parser.add_argument('width', type=float, help='Width of rectangle to plot')
        rectangle_parser.add_argument('height', type=float, help='Height of rectangle to plot')
        rectangle_parser.add_argument('--angle', type=float, help='Angle of rectangle to plot', default=0.0,
                                      required=False)
    
        ellipse_parser = figure_subparser.add_parser('ellipse')
        ellipse_parser.add_argument('width', type=float, help='Width of ellipse to plot')
        ellipse_parser.add_argument('height', type=float, help='Height of ellipse to plot')
        ellipse_parser.add_argument('--angle', type=float, help='Angle of ellipse to plot', default=0.0,
                                    required=False)

    def parse(self):
        self.script_args = self.parser.parse_args()

    def check_args(self):
        if self.script_args is None:
            self.parse()

        if self.script_args.outputtype == 'file':
            if self.script_args.outputfile is None:
                self.parser.error(
                    f'-o must be specified if output type is file'
                )
            else:
                extension = self.script_args.outputfile.suffix.split('.')[-1]

                if not extension:
                    self.parser.error(
                        'Please specify file extension\n'
                        f'Supported extensions: {", ".join(SUPPORTED_FILE_TYPES)}'
                    )

                elif extension not in SUPPORTED_FILE_TYPES:
                    self.parser.error(
                        f'{extension.upper()} file format is not supported by matplotlib\n'
                        f'Supported extensions: {", ".join(SUPPORTED_FILE_TYPES)}'
                    )

    @classmethod
    def check_and_get_args(cls):
        args_parser = cls()

        args_parser.check_args()

        return args_parser.script_args


def main():
    script_args = ArgsParser.check_and_get_args()

    plot_args = (script_args.x, script_args.y)
    plot_kwargs = {
        'output_type': script_args.outputtype,
        'output_file_path': script_args.outputfile,
    }

    if script_args.figuretype == 'circle':
        CirclePlotter.run(
            *plot_args,
            radius=script_args.radius,
            **plot_kwargs
        )

    elif script_args.figuretype == 'rectangle':
        RectanglePlotter.run(
            *plot_args,
            width=script_args.width,
            height=script_args.height,
            angle=script_args.angle,
            **plot_kwargs
        )

    elif script_args.figuretype == 'ellipse':
        EllipsePlotter.run(
            *plot_args,
            width=script_args.width,
            height=script_args.height,
            angle=script_args.angle,
            **plot_kwargs
        )


if __name__ == '__main__':
    main()
