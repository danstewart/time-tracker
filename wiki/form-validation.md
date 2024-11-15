`app/lib/validate.py` and `app/static/js/form.js` provide a simple way to validate form submissions.  

You can auto connect validation to all forms on a page using the following snippet:
```html
<script type="module">
    import { autoAttachValidation } from "/static/js/form.js";
    window.addEventListener("DOMContentLoaded", () => autoAttachValidation());
</script>
```

Or a single form using:
```html
<script type="module">
    import { attachValidation } from "/static/js/form.js";
    window.addEventListener("DOMContentLoaded", () => attachValidation(document.querySelector("#my-form")));
</script>
```

And here is how to use it on the python side to actually validate the form:
```python
@v.route("/settings", methods=["GET", "POST"])
def general_settings():
    if request.form:
        from flask import flash, redirect

        if request.form.get("validate"):
            from app.lib import validate as v

            validation = v.validate_form(
                values=dict(request.form),
                checks={
                    "timezone": v.Check(regex=r"\w+\/\w+"),
                    "holiday_location": v.Check(options=["GB/ENG", "GB/NIR", "GB/WLS", "GB/SCT"]),
                    "week_start": v.Check(options=["0", "1", "2", "3", "4", "5", "6"]),
                    "hours_per_day": v.Check(
                        func=lambda x: Decimal(x) > 0,
                        message="Must be a positive number",
                    ),
                },
            )
            return validation.errors or validation.success

        settings.update(**request.form)
        flash("Settings saved.", "success")
        return redirect("/dash")

    return render("pages/settings.html.j2", settings=settings.fetch(), page="general")
```

When the form is submitted it will first submit via JavaScript with the parameter `validate=1` and hit our validation logic, which should return JSON.  
Any errors will be displayed on the form or if the validation passes then the form will be submitted normally.  

The `checks` support
- `regex`: A regex to match the value against
- `options`: A list of options to match against
- `func`: A function to call with the value, if it returns `False` then the error message is displayed
- `message`: The error message to display if the check fails
