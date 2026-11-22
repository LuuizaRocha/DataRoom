import pandas as pd
from core.profiler import profile_dataframe

def test_profile_counts_missing_and_duplicates():
    df = pd.DataFrame({"a":[1,1,None], "b":["x","x","y"]})
    result = profile_dataframe(df)
    assert result["rows"] == 3
    assert result["columns"] == 2
    assert result["missing"] == 1
    assert result["duplicate_rows"] == 1
