import arrow
from app.lib.util.date import calculate_expected_hours


def test_one_work_day():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-01'),  # Friday
        end=arrow.get('2021-01-01'),  # Friday
        hours_per_day=7.5,
    )

    assert(hours == 7.5)


def test_weekend():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-02'),  # Saturday
        end=arrow.get('2021-01-03'),  # Sunday
        hours_per_day=7.5,
    )

    assert(hours == 0)


def test_wed_to_wed():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-06'),  # Wednesday
        end=arrow.get('2021-01-13'),  # Wednesday
        hours_per_day=7.5,
    )

    assert(hours == 45)


def test_fri_to_sun():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-08'),  # Wednesday
        end=arrow.get('2021-01-10'),  # Wednesday
        hours_per_day=7.5,
    )

    assert(hours == 7.5)


def test_sun_to_sat():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-10'),  # Sunday
        end=arrow.get('2021-01-16'),  # Saturday
        hours_per_day=7.5,
    )

    assert(hours == 37.5)


def test_sun_to_sun():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-10'),  # Sunday
        end=arrow.get('2021-01-17'),  # Sunday
        hours_per_day=7.5,
    )

    assert(hours == 37.5)


def test_large_range():
    hours = calculate_expected_hours(
        start=arrow.get('2021-01-12'),  # Tuesday
        end=arrow.get('2021-03-28'),  # Sunday
        hours_per_day=7.5,
    )

    assert(hours == 405)  # 54 days
