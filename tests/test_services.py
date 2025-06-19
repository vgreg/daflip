import pandas as pd
import pytest

from src.daflip.services import convert_data


@pytest.mark.parametrize(
    "fmt,ext,read_func,write_func",
    [
        ("csv", ".csv", pd.read_csv, pd.DataFrame.to_csv),
        ("parquet", ".parquet", pd.read_parquet, pd.DataFrame.to_parquet),
        ("feather", ".feather", pd.read_feather, pd.DataFrame.to_feather),
    ],
)
def test_convert_roundtrip(fmt, ext, read_func, write_func, tmp_path):
    # Create a simple DataFrame
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    input_file = tmp_path / f"input{ext}"
    output_file = tmp_path / f"output{ext}"
    # Write input file
    if fmt == "csv":
        df.to_csv(input_file, index=False)
    elif fmt == "parquet":
        df.to_parquet(input_file, index=False)
    elif fmt == "feather":
        df.to_feather(input_file, index=False)
    # Convert
    convert_data(str(input_file), str(output_file))
    # Read output and compare
    df2 = read_func(output_file)
    pd.testing.assert_frame_equal(df, df2, check_dtype=False)


def test_convert_row_selection(tmp_path):
    df = pd.DataFrame({"a": range(10)})
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    df.to_csv(input_file, index=False)
    convert_data(str(input_file), str(output_file), rows="2:5")
    df2 = pd.read_csv(output_file)
    assert df2.shape[0] == 3
    assert df2["a"].tolist() == [2, 3, 4]


def test_convert_unsupported_format(tmp_path):
    input_file = tmp_path / "input.unsupported"
    output_file = tmp_path / "output.csv"
    with open(input_file, "w") as f:
        f.write("dummy")
    with pytest.raises(ValueError):
        convert_data(str(input_file), str(output_file))


def test_convert_fixed_not_implemented(tmp_path):
    input_file = tmp_path / "input.fixed"
    output_file = tmp_path / "output.csv"
    with open(input_file, "w") as f:
        f.write("dummy")
    with pytest.raises(NotImplementedError):
        convert_data(str(input_file), str(output_file))
