from VERAStatus.Weather import wind_direction2octas


def test_wind_direction2octas():
    assert wind_direction2octas(45.0) == "NE"
    assert wind_direction2octas(-50.0) == "NW"
    assert wind_direction2octas(500.0) == "SE"
