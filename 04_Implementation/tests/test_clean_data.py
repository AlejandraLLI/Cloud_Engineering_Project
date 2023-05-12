import pytest
import numpy as np
import src.clean_data as cd

# Happy path tests
@pytest.mark.parametrize(
    "text,expected",
    [
        ("2.50h m", 2.5), 
        ("10.30h m", 10.3),
        ("3h 30m", 3.5),
        ("1h 45m", 1.75),
    ],
)
def test_get_duration_happy_path(text, expected):
    assert cd.get_duration(text) == expected


# Unhappy path tests
@pytest.mark.parametrize(
    "text",
    [
        "2.5", 
        "10h", 
        "3h m", 
        "abcd",
        "",
    ],
)
def test_get_duration_unhappy_path(text):
    with pytest.raises(Exception):
        cd.get_duration(text)


# Define a common stop dictionary for the tests
@pytest.fixture
def setup_stops():
    # Stop dict
    stop_dict = {"non-stop": 0,
                 "1-stop": 1,
                 "2+-stop": 2}
    return stop_dict


# Happy path tests
@pytest.mark.parametrize(
    "text, expected",
    [
        ("non-stop", 0), 
        ("1-stop", 1),
        ("2+-stops", 2),
        ("3 stops", np.nan)
    ],
)
def test_get_stops_happy_path(setup_stops, text, expected):
    # Define a common regex pattern for the tests
    pattern = r'non-stop|1-stop|2\+-stop'
    result = cd.get_stops(text, pattern, setup_stops)

    if np.isnan(expected):
        assert np.isnan(result)
    else:
        assert result == expected


# Unhappy path tests
@pytest.mark.parametrize(
    "text",
    [
        "stop", 
        "stops", 
        "1", 
        "2",
        "",
    ],
)
def test_get_stops_unhappy_path(setup_stops, text):
    pattern = r'non-stop|1-stop|2\+-stop'
    assert np.isnan(cd.get_stops(text,pattern,setup_stops))


# Set hours dictionary
@pytest.fixture
def set_bucketDict(): 
    hour_buckets = {
            "early_morning": {"min": 4, "max": 8},
            "morning": {"min": 6, "max": 12},        
            "afternoon": {"min": 12, "max": 16},
            "evening": {"min": 16, "max": 20},
            "night": {"min": 20, "max": 24},
            "late_night":{"min": 0, "max": 4}
        }
    return hour_buckets

# Happy path tests
@pytest.mark.parametrize(
    "time, expected",
    [
        ("00:00", "late_night"), 
        ("06:20", "morning"),
        ("12:08", "afternoon"),
        ("18:43", "evening"),
        ("04:38", "early_morning"),
        ("12:00", "afternoon")
    ],
)
def test_bucket_hours_happy_path(set_bucketDict, time, expected):
    assert cd.bucket_hours(time, set_bucketDict) == expected

# Unhappy path tests
@pytest.mark.parametrize(
    "time",
    [
        "25:00", 
        "60:00", 
        "100:00",
        "",
    ],
)
def test_bucket_hours_unhappy_path(time):
    with pytest.raises(Exception):
        cd.bucket_hours(time, set_bucketDict)
