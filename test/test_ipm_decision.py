import openalea.weatherdata.wrapper.ipm_decision as ipm_decision

def test_get_data():
    df = ipm_decision.get_data()
    assert len(df) == 213
    assert '1001' in df.columns