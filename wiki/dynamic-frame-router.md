The `DynamicFrameRouter` component is used handle routing within a `DynamicFrame` component.

Here is an example of how it might be used within a jinja template:

```html
{% extends "layouts/wrapper.html.j2" %}

{% block content %}
    <div class="row">
        <div class="col-lg-2 mt-1 pe-5 pb-3">
            <dynamic-frame-router :target="#main-content" :caching>
                <nav class="nav nav-pills flex-lg-column">
                    <a class="nav-link{% if page == 'upcoming' %} active{% endif %}"
                        aria-current="page"
                        href="/holidays/upcoming">Upcoming</a>
                    <a class="nav-link{% if page == 'history' %} active{% endif %}"
                        href="/holidays/history">History</a>
                </nav>
            </dynamic-frame-router>
        </div>

        <div class="col">
            <!-- We don't load on init here so we can do the initial load server side using jinjas include -->
            <dynamic-frame id="main-content" :url="/holidays/{{ page }}" :param-block="frame" :render-on-init="0">
                <!-- We wrap this in a block as that allows us to load just this section via /settings/general?block=frame -->
                {% block frame %}
                    {% include "frames/holidays/" + page + ".html.j2" %}
                {% endblock frame %}
            </dynamic-frame>
        </div>
    </div>
{% endblock content %}
```

And here is the view handler:
```python
from app.lib.blocks import frame, render

@v.get("/holidays")
@v.get("/holidays/upcoming")
def upcoming_holidays():
    _settings = settings.fetch()

    return render(
        "pages/holidays.html.j2",
        page="upcoming",
        upcoming_holidays=holidays.get_upcoming_holidays(),
    )
```


The `dynamic-frame-router` element wraps the anchor elements that should update the `DynamicFrame` component (controlled by the `:target` attribute).  
The `:caching` attribute is used to enable caching of the content of the `DynamicFrame` component, so if you navigate back to a page previously visited then the content will be loaded from the cache instead of making a new request.  

In the template the `{% block frame %}` section is used to load the frame content on initial page load from the server, instead of loading via JavaScript.  
This means if we go to `/holidays` or `/holidays/upcoming` then it's just a plain load from the server, then when you navigate after load only the frame is updated using JavaScript.

The view should use `render()` instead of `render_template()`, where the first argument is the whole page template.
When the route is called with the `?block=` querystring parameter then the only the specified block from within that template is returned (in this case the block named `frame`).   

