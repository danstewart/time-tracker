# TODO: Add tests
def test_calculate_expected_hours():
    import arrow
    from app.lib.util.date import calculate_expected_hours

    hours = calculate_expected_hours(
        start=arrow.get('2021-01-01'),
        end=arrow.get('2021-01-01'),
        hours_per_day=7.5,
    )

    assert(hours == 0)
