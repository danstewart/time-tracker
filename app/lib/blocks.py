"""
blocks.py
---
This module contains the logic needed to render blocks of a template and helpers to make it easier.

```python3
from app.lib.blocks import render, frame

@frame
@v.get("/greeter")
def some_route():
    return render("hello.html", name="Dan")
```

Calling `/greeter?block=greeting` will render only the `greeting` block within `hello.html`.
"""

import typing
from functools import wraps

from blinker import Namespace
from flask import current_app, render_template
from jinja2 import Environment


class BlockNotFoundError(Exception):
    """
    The exception raised when the requested block does not exist.
    """

    def __init__(self, block_name: str, template_name: str, message: typing.Optional[str] = None):
        self.block_name = block_name
        self.template_name = template_name
        super().__init__(message or f"Block {self.block_name!r} not found in template {self.template_name!r}")


def _render_block(
    environment: Environment,
    template_name: str,
    block_name: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """This returns the rendered template block as a string."""
    template = environment.get_template(template_name)
    try:
        block_render_func = template.blocks[block_name]
    except KeyError:
        raise BlockNotFoundError(block_name, template_name)

    ctx = template.new_context(dict(*args, **kwargs))
    try:
        return environment.concat(block_render_func(ctx))  # type: ignore
    except Exception:
        environment.handle_exception()


jinja2_fragments_signals = Namespace()
before_render_template_block = jinja2_fragments_signals.signal("before-render-template-block")
template_block_rendered = jinja2_fragments_signals.signal("template-block-rendered")


def render_block(template_name: str, block_name: str, **replacers) -> str:
    """
    Like `flask.templating.render_template` but renders only a single block within the template.

    `template_name`: The name of the template to render
    `block_name`: The name of the jinja block within that template to render
    `replacers`: Any values to replace into the template
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    app.update_template_context(replacers)
    before_render_template_block.send(app, template_name=template_name, block_name=block_name, context=replacers)
    rendered = _render_block(app.jinja_env, template_name, block_name, **replacers)
    template_block_rendered.send(app, template_name=template_name, block_name=block_name, context=replacers)
    return rendered


def frame(f) -> typing.Any:
    """
    View decorator that adds support for rendering the route with a `?block` query string argument to render a single block.
    Expects the wrapped function to return a `RenderIntent`.
    """

    @wraps(f)
    def decorated(*args, **kwargs) -> str:
        from flask import request

        intent = f(*args, **kwargs)

        if not isinstance(intent, RenderIntent):
            return intent

        if block := request.args.get("block"):
            intent.block = block

        return intent.execute()

    return decorated


class RenderIntent:
    """
    A RenderIntent is a simple object that contains the information needed to render a view.
    """

    def __init__(self, template: str, block: typing.Optional[str] = None, **replacers):
        self.template = template
        self.block = block
        self.replacers = replacers

    def execute(self) -> str:
        if self.block:
            return render_block(self.template, self.block, **self.replacers)

        return render_template(self.template, **self.replacers)


def render(template: str, block: typing.Optional[str] = None, **replacers) -> RenderIntent:
    """
    Drop in replacement for `flask.templating.render_template` but instead of rendering a template it returns a `RenderIntent`.
    This is what is expcected by the `@frame` decorator.
    Your decorated view function should use `render()` instead of `render_template()`.
    """
    return RenderIntent(template, block, **replacers)
