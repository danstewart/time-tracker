# Stolen from https://github.com/sponsfreixes/jinja2-fragments

import typing

from blinker import Namespace
from flask import current_app
from jinja2 import Environment


class BlockNotFoundError(Exception):
    def __init__(self, block_name: str, template_name: str, message: typing.Optional[str] = None):
        self.block_name = block_name
        self.template_name = template_name
        super().__init__(message or f"Block {self.block_name!r} not found in template {self.template_name!r}")


async def _render_block_async(
    environment: Environment,
    template_name: str,
    block_name: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """
    This works similar to :func:`render_block` but returns a coroutine that when
    awaited returns the entire rendered template block string. This requires the
    environment async feature to be enabled.
    """
    if not environment.is_async:
        raise RuntimeError("The environment was not created with async mode enabled.")

    template = environment.get_template(template_name)
    try:
        block_render_func = template.blocks[block_name]
    except KeyError:
        raise BlockNotFoundError(block_name, template_name)

    ctx = template.new_context(dict(*args, **kwargs))
    try:
        return environment.concat(  # type: ignore
            [n async for n in block_render_func(ctx)]  # type: ignore
        )
    except Exception:
        return environment.handle_exception()


def _render_block(
    environment: Environment,
    template_name: str,
    block_name: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> str:
    """This returns the rendered template block as a string."""
    if environment.is_async:
        import asyncio

        close = False

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            close = True

        try:
            return loop.run_until_complete(_render_block_async(environment, template_name, block_name, *args, **kwargs))
        finally:
            if close:
                loop.close()

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


def render_block(template_name: str, block_name: str, **context: typing.Any) -> str:
    """Renders a template's block from the template folder with the given context.

    :param template_name: the name of the template where to find the block to be
        rendered
    :param block_name: the name of the block to be rendered
    :param context: the variables that should be available in the context of the block
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    app.update_template_context(context)
    before_render_template_block.send(app, template_name=template_name, block_name=block_name, context=context)
    rendered = _render_block(app.jinja_env, template_name, block_name, **context)
    template_block_rendered.send(app, template_name=template_name, block_name=block_name, context=context)
    return rendered
