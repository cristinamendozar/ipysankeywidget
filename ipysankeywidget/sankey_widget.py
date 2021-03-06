import warnings
import base64

import ipywidgets as widgets
from traitlets import (
    Float,
    Dict,
    List,
    Bool,
    observe,
    Unicode,
)


@widgets.register
class SankeyWidget(widgets.DOMWidget):
    """Sankey widget"""
    _view_name = Unicode('SankeyView').tag(sync=True)
    _model_name = Unicode('SankeyModel').tag(sync=True)
    _view_module = Unicode('jupyter-sankey-widget').tag(sync=True)
    _model_module = Unicode('jupyter-sankey-widget').tag(sync=True)
    _view_module_version = Unicode('^0.2.3').tag(sync=True)
    _model_module_version = Unicode('^0.2.3').tag(sync=True)

    links = List([]).tag(sync=True)
    nodes = List([]).tag(sync=True)
    order = List(None, allow_none=True).tag(sync=True)
    groups = List([]).tag(sync=True)

    # Options
    rank_sets = List([]).tag(sync=True)
    align_link_types = Bool(False).tag(sync=True)
    scale = Float(None, allow_none=True).tag(sync=True)
    margins = Dict({}).tag(sync=True)

    # Get raster image data back
    png = Unicode('').tag(sync=True)

    # get vector image back
    svg = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):
        """Constructor"""

        # Automatically create nodes
        nodes = kwargs.get('nodes', [])
        node_ids = {node['id'] for node in nodes}
        missing_ids = set()
        for link in kwargs.get('links', []):
            if link['source'] not in node_ids:
                missing_ids.add(link['source'])
            if link['target'] not in node_ids:
                missing_ids.add(link['target'])
        kwargs['nodes'] = nodes + [{'id': k} for k in missing_ids]

        super(SankeyWidget, self).__init__(**kwargs)
        self._selected_handlers = widgets.CallbackDispatcher()
        self._auto_png_filename = None
        self._auto_svg_filename = None
        self.on_msg(self._handle_sankey_msg)

    def on_selected(self, callback, remove=False):
        """Register a callback to execute when a node is selected.

        The callback will be called with one argument,
        the Sankey widget instance.

        Parameters
        ----------
        remove : bool (optional)
            Set to true to remove the callback from the list of callbacks."""
        self._selected_handlers.register_callback(callback, remove=remove)

    def _handle_sankey_msg(self, _, content, buffers):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if content.get('event', '') == 'selected':
            self._selected_handlers(self, content.get('node'))

    @observe("png")
    def _on_png_data(self, change):
        if change['type'] != 'change':
            return
        if self._auto_png_filename:
            self.save_png(self._auto_png_filename)
            self._auto_png_filename = None

    def save_png(self, filename):
        """Save the diagram to a PNG file.

        The widget must be displayed first before the PNG data is available. To
        display the widget and save an image at the same time, use
        `auto_save_png`.

        Parameters
        ----------
        filename : string
        """
        if self.png:
            data = base64.decodebytes(bytes(self.png, 'ascii'))
            with open(filename, 'wb') as f:
                f.write(data)
        else:
            warnings.warn('No png image available! Try auto_save_png() instead?')

    def auto_save_png(self, filename):
        """Save the diagram to a PNG file, once it has been rendered.

        This waits for the diagram to be rendered, then automatically calls
        `save_png` for you.

        Parameters
        ----------
        filename : string
        """
        self._auto_png_filename = filename
        return self

    @observe("svg")
    def _on_svg_data(self, change):
        if change['type'] != 'change':
            return
        if self._auto_svg_filename:
            self.save_svg(self._auto_svg_filename)
            self._auto_svg_filename = None

    def save_svg(self, filename):
        """Save the diagram to an SVG file.

        The widget must be displayed first before the SVG data is available. To
        display the widget and save an image at the same time, use
        `auto_save_svg`.

        Parameters
        ----------
        filename : string
        """
        if self.svg:
            with open(filename, 'wb') as f:
                f.write(self.svg.encode('utf8'))
        else:
            warnings.warn('No svg image available! Try auto_save_svg() instead?')

    def auto_save_svg(self, filename):
        """Save the diagram to an SVG file, once it has been rendered.

        This waits for the diagram to be rendered, then automatically calls
        `save_svg` for you.

        Parameters
        ----------
        filename : string
        """
        self._auto_svg_filename = filename
        return self
