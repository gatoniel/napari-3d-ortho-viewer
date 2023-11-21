# napari-3d-ortho-viewer

[![License](https://img.shields.io/pypi/l/napari-3d-ortho-viewer.svg?color=green)](https://github.com/gatoniel/napari-3d-ortho-viewer/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-3d-ortho-viewer.svg?color=green)](https://pypi.org/project/napari-3d-ortho-viewer)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-3d-ortho-viewer.svg?color=green)](https://python.org)
[![tests](https://github.com/gatoniel/napari-3d-ortho-viewer/workflows/tests/badge.svg)](https://github.com/gatoniel/napari-3d-ortho-viewer/actions)
[![codecov](https://codecov.io/gh/gatoniel/napari-3d-ortho-viewer/branch/main/graph/badge.svg)](https://codecov.io/gh/gatoniel/napari-3d-ortho-viewer)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-3d-ortho-viewer)](https://napari-hub.org/plugins/napari-3d-ortho-viewer)

Napari 3D Ortho Viewer - an ortho viewer for napari for 3D images

----------------------------------

https://github.com/gatoniel/napari-3d-ortho-viewer/assets/40384506/4296dc11-ea37-40a0-8b17-eeb77480672f

This plugin is heavily inspired by [ortho-view-napari].

Check out this post on image.sc (https://forum.image.sc/t/napari-visualization-in-3-planes/57768) for more infos about multiview support in [napari].

This viewer has some additional features:
- double click to jump to specific position in all slices
- additional 3d view of 3d stack with lines or planes indicating current position

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/docs/plugins/index.html
-->

## Installation

You can install `napari-3d-ortho-viewer` via [pip]:

    pip install napari-3d-ortho-viewer



To install latest development version :

    pip install git+https://github.com/gatoniel/napari-3d-ortho-viewer.git


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-3d-ortho-viewer" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/gatoniel/napari-3d-ortho-viewer/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
[ortho-view-napari]: https://github.com/JoOkuma/ortho-view-napari
