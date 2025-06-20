"""
Data conversion services.

This module provides services for converting data between different formats
using pandas and pyarrow. It supports both chunked and non-chunked processing
for large datasets.
"""

import json
from typing import Dict, Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

from .models import SupportedInputFormat, SupportedOutputFormat
from .utils import infer_format

console = Console()

# Supported pandas read/write kwargs for each format
READ_KWARGS = {
    SupportedInputFormat.CSV.value: ["sep", "dtype_backend"],
    SupportedInputFormat.TSV.value: ["sep", "dtype_backend"],
    SupportedInputFormat.PSV.value: ["sep", "dtype_backend"],
    SupportedInputFormat.FIXED.value: ["colspecs", "dtype_backend"],
    SupportedInputFormat.PARQUET.value: ["dtype_backend"],
    SupportedInputFormat.ORC.value: ["dtype_backend"],
    SupportedInputFormat.FEATHER.value: ["dtype_backend"],
    SupportedInputFormat.SAS.value: [],
    SupportedInputFormat.STATA.value: [],
    SupportedInputFormat.SPSS.value: [],
    SupportedInputFormat.EXCEL.value: ["sheet_name", "dtype_backend"],
    SupportedInputFormat.HTML.value: ["match", "header", "index_col"],
}

WRITE_KWARGS = {
    SupportedOutputFormat.CSV.value: ["sep", "compression", "index"],
    SupportedOutputFormat.PARQUET.value: ["compression", "compression_level", "index"],
    SupportedOutputFormat.ORC.value: ["compression", "index"],
    SupportedOutputFormat.FEATHER.value: ["compression", "compression_level", "index"],
    SupportedOutputFormat.EXCEL.value: ["sheet_name", "index"],
    SupportedOutputFormat.STATA.value: ["compression", "index"],
}

SEP_MAP = {
    "csv": ",",
    "tsv": "\t",
    "psv": "|",
}

# Supported chunked formats
CHUNKED_READ_FORMATS = {"csv", "sas7bdat"}
CHUNKED_WRITE_FORMATS = {"csv", "parquet"}  # feather does not support append


def _show_preview(df: pd.DataFrame, msg: str = "Data preview"):
    """Display a preview of the dataframe using rich tables.

    Args:
        df: The dataframe to preview
        msg: The title message for the preview table
    """
    table = Table(title=msg)
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.head(5).iterrows():
        table.add_row(*[str(x) for x in row])
    console.print(table)


def _load_schema(schema_file: str):
    """Load schema from JSON file.

    Args:
        schema_file: Path to the JSON schema file

    Returns:
        pyarrow.Schema: The loaded schema object

    Raises:
        FileNotFoundError: If the schema file doesn't exist
        json.JSONDecodeError: If the schema file contains invalid JSON
        ValueError: If the schema structure is invalid
    """
    import pyarrow as pa

    # Map string type names to PyArrow types
    type_mapping = {
        "int8": pa.int8(),
        "int16": pa.int16(),
        "int32": pa.int32(),
        "int64": pa.int64(),
        "uint8": pa.uint8(),
        "uint16": pa.uint16(),
        "uint32": pa.uint32(),
        "uint64": pa.uint64(),
        "float16": pa.float16(),
        "float32": pa.float32(),
        "float64": pa.float64(),
        "double": pa.float64(),  # PyArrow exports float64 as "double"
        "string": pa.string(),
        "binary": pa.binary(),
        "bool": pa.bool_(),
        "date32": pa.date32(),
        "date64": pa.date64(),
        "timestamp": pa.timestamp("us"),
        "time32": pa.time32("s"),
        "time64": pa.time64("us"),
    }

    with open(schema_file, "r") as f:
        schema_json = json.load(f)
        fields = []
        for f in schema_json["fields"]:
            type_name = f["type"]
            if type_name not in type_mapping:
                raise ValueError(f"Unsupported type: {type_name}")
            fields.append(pa.field(f["name"], type_mapping[type_name]))
        return pa.schema(fields)


def _validate_chunking_support(
    input_format: str,
    output_format: str,
    input_chunk_size: Optional[int],
    output_chunk_size: Optional[int],
):
    """Validate that the specified formats support chunking.

    Args:
        input_format: The input file format
        output_format: The output file format
        input_chunk_size: Size of input chunks (None if not chunked)
        output_chunk_size: Size of output chunks (None if not chunked)

    Raises:
        NotImplementedError: If chunking is not supported for the specified formats
    """
    if input_chunk_size and input_format not in CHUNKED_READ_FORMATS:
        raise NotImplementedError(
            f"Chunked reading is not supported for input format: {input_format}"
        )
    if output_chunk_size and output_format not in CHUNKED_WRITE_FORMATS:
        raise NotImplementedError(
            f"Chunked writing is not supported for output format: {output_format}"
        )


def _create_chunked_reader(
    input_file: str,
    input_format: str,
    input_chunk_size: int,
    sas_encoding: Optional[str],
):
    """Create a chunked reader for the input file.

    Args:
        input_file: Path to the input file
        input_format: The input file format
        input_chunk_size: Size of chunks to read
        sas_encoding: Encoding for SAS files (None for bytes, "utf-8" for text)

    Returns:
        Iterator[pd.DataFrame]: A chunked reader iterator

    Raises:
        NotImplementedError: If chunked reading is not implemented for the format
    """
    if input_format == "csv":
        return pd.read_csv(
            input_file, chunksize=input_chunk_size, dtype_backend="pyarrow"
        )
    elif input_format == "sas7bdat":
        return pd.read_sas(
            input_file, chunksize=input_chunk_size, encoding=sas_encoding
        )
    else:
        raise NotImplementedError(
            f"Chunked reading is not implemented for {input_format}"
        )


def _write_chunk_csv(chunk: pd.DataFrame, output_file: str, first: bool):
    """Write a chunk to CSV file.

    Args:
        chunk: The dataframe chunk to write
        output_file: Path to the output CSV file
        first: Whether this is the first chunk (determines write mode and header)
    """
    chunk.to_csv(
        output_file,
        mode="w" if first else "a",
        header=first,
        index=False,
    )


def _write_chunk_parquet(
    chunk: pd.DataFrame, output_file: str, first: bool, pqwriter=None
):
    """Write a chunk to Parquet file.

    Args:
        chunk: The dataframe chunk to write
        output_file: Path to the output Parquet file
        first: Whether this is the first chunk
        pqwriter: Existing ParquetWriter instance (None for first chunk)

    Returns:
        pyarrow.parquet.ParquetWriter: The ParquetWriter instance
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.Table.from_pandas(chunk)
    if first:
        pqwriter = pq.ParquetWriter(output_file, table.schema)
    pqwriter.write_table(table)
    return pqwriter


def _handle_chunked_conversion(
    input_file: str,
    output_file: str,
    input_format: str,
    output_format: str,
    input_chunk_size: int,
    sas_encoding: Optional[str],
):
    """Handle chunked data conversion.

    Args:
        input_file: Path to the input file
        output_file: Path to the output file
        input_format: The input file format
        output_format: The output file format
        input_chunk_size: Size of input chunks
        sas_encoding: Encoding for SAS files
    """
    reader = _create_chunked_reader(
        input_file, input_format, input_chunk_size, sas_encoding
    )

    first = True
    pqwriter = None

    for chunk in reader:
        if output_format == "csv":
            _write_chunk_csv(chunk, output_file, first)
        elif output_format == "parquet":
            pqwriter = _write_chunk_parquet(chunk, output_file, first, pqwriter)
        first = False

    if output_format == "parquet" and pqwriter:
        pqwriter.close()


def _build_read_kwargs(
    input_format: str, sheet_name: Optional[str], table_number: Optional[int]
):
    """Build read kwargs for non-chunked reading.

    Args:
        input_format: The input file format
        sheet_name: Sheet name for Excel files
        table_number: Table number for HTML files

    Returns:
        Dict: Dictionary of read parameters

    Raises:
        NotImplementedError: If the format is not yet implemented
    """
    read_kwargs = {"dtype_backend": "pyarrow"}

    if input_format in SEP_MAP:
        read_kwargs["sep"] = SEP_MAP[input_format]

    if input_format == "fixed":
        raise NotImplementedError("Fixed-width file support is not yet implemented.")

    if input_format in ["excel", "xlsx", "xls"] and sheet_name:
        read_kwargs["sheet_name"] = sheet_name
    if input_format == "xls":
        read_kwargs["engine"] = "xlrd"

    if input_format == "html" and table_number is not None:
        read_kwargs["match"] = None
        read_kwargs["flavor"] = "bs4"
        read_kwargs["header"] = 0
        read_kwargs["index_col"] = None

    return read_kwargs


def _read_dataframe(
    input_file: str,
    input_format: str,
    read_kwargs: Dict,
    sas_encoding: Optional[str],
    table_number: Optional[int],
    schema: Optional[object] = None,
):
    """Read dataframe from file based on format.

    Args:
        input_file: Path to the input file
        input_format: The input file format
        read_kwargs: Dictionary of read parameters
        sas_encoding: Encoding for SAS files
        table_number: Table number for HTML files
        schema: Optional PyArrow schema to use for reading

    Returns:
        pd.DataFrame: The loaded dataframe

    Raises:
        ValueError: If the input format is not supported
    """
    if input_format == "csv" or input_format in SEP_MAP:
        if schema:
            try:
                import pyarrow.csv as csv

                arrow_kwargs = {}
                if "sep" in read_kwargs:
                    arrow_kwargs["delimiter"] = read_kwargs["sep"]
                if "header" in read_kwargs:
                    arrow_kwargs["header"] = read_kwargs["header"]
                table = csv.read_csv(input_file, schema=schema, **arrow_kwargs)
                return table.to_pandas()
            except TypeError:
                # Fallback: read with pandas, then apply schema manually
                df = pd.read_csv(input_file, **read_kwargs)
                # Apply datetime conversion for columns defined as timestamp in schema
                for field in schema:
                    if str(field.type).startswith("timestamp"):
                        df[field.name] = pd.to_datetime(df[field.name])
                return df
        else:
            return pd.read_csv(input_file, **read_kwargs)
    elif input_format == "parquet":
        return pd.read_parquet(input_file, **read_kwargs)
    elif input_format == "orc":
        return pd.read_orc(input_file, **read_kwargs)
    elif input_format == "feather":
        return pd.read_feather(input_file, **read_kwargs)
    elif input_format == "sas7bdat":
        return pd.read_sas(input_file, encoding=sas_encoding)
    elif input_format == "stata":
        return pd.read_stata(input_file)
    elif input_format == "spss":
        return pd.read_spss(input_file)
    elif input_format in ["excel", "xlsx"]:
        return pd.read_excel(input_file, **read_kwargs)
    elif input_format == "xls":
        # Ensure engine is set to xlrd for .xls files
        read_kwargs = {**read_kwargs, "engine": "xlrd"}
        return pd.read_excel(input_file, **read_kwargs)
    elif input_format == "html":
        dfs = pd.read_html(input_file, **read_kwargs)
        if table_number is not None and 0 <= table_number < len(dfs):
            return dfs[table_number]
        else:
            return dfs[0]
    else:
        raise ValueError(f"Unsupported input format: {input_format}")


def _apply_row_selection(df: pd.DataFrame, rows: Optional[str]):
    """Apply row selection to dataframe.

    Args:
        df: The dataframe to filter
        rows: Row selection string in format "start:end" (e.g., "0:100")

    Returns:
        pd.DataFrame: The filtered dataframe (original if no selection or invalid)
    """
    if not rows:
        return df

    try:
        start, end = map(int, rows.split(":"))
        return df.iloc[start:end]
    except Exception:
        console.print(
            f"[yellow]Warning: Could not parse rows '{rows}', ignoring row selection."
        )
        return df


def _convert_dtypes(df: pd.DataFrame):
    """Convert dataframe dtypes to pyarrow.

    Args:
        df: The dataframe to convert

    Returns:
        pd.DataFrame: The dataframe with pyarrow dtypes
    """
    if hasattr(df, "convert_dtypes"):
        return df.convert_dtypes(dtype_backend="pyarrow")
    return df


def _build_write_kwargs(
    compression: Optional[str],
    compression_level: Optional[int],
    sheet_name: Optional[str],
    output_format: str,
):
    """Build write kwargs for output.

    Args:
        compression: Compression type (e.g., "gzip", "snappy")
        compression_level: Compression level (1-9 for gzip)
        sheet_name: Sheet name for Excel files
        output_format: The output file format

    Returns:
        Dict: Dictionary of write parameters
    """
    write_kwargs = {}

    if compression:
        write_kwargs["compression"] = compression
    if compression_level is not None:
        write_kwargs["compression_level"] = compression_level
    if sheet_name and output_format in ["excel", "xlsx", "xls"]:
        write_kwargs["sheet_name"] = sheet_name
    if output_format == "xls":
        write_kwargs["engine"] = "xlwt"

    return write_kwargs


def _write_dataframe(
    df: pd.DataFrame, output_file: str, output_format: str, write_kwargs: Dict
):
    """Write dataframe to file based on format.

    Args:
        df: The dataframe to write
        output_file: Path to the output file
        output_format: The output file format
        write_kwargs: Dictionary of write parameters

    Raises:
        ValueError: If the output format is not supported
    """
    if output_format == "csv":
        write_kwargs["sep"] = ","
        df.to_csv(output_file, index=False, **write_kwargs)
    elif output_format == "parquet":
        df.to_parquet(output_file, index=False, **write_kwargs)
    elif output_format == "orc":
        df.to_orc(output_file, index=False, **write_kwargs)
    elif output_format == "feather":
        df.to_feather(output_file, **write_kwargs)
    elif output_format in ["excel", "xlsx", "xls"]:
        df.to_excel(output_file, index=False, **write_kwargs)
    elif output_format == "stata":
        # stata doesn't support index parameter
        df.to_stata(output_file, **write_kwargs)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def convert_data(
    input_file: str,
    output_file: str,
    input_format: Optional[str] = None,
    output_format: Optional[str] = None,
    compression: Optional[str] = None,
    compression_level: Optional[int] = None,
    rows: Optional[str] = None,
    sheet_name: Optional[str] = None,
    table_number: Optional[int] = None,
    sas_keep_bytes: bool = False,
    input_chunk_size: Optional[int] = None,
    output_chunk_size: Optional[int] = None,
    schema_file: Optional[str] = None,
    config: Optional[Dict] = None,
):
    """Convert data from one format to another using pandas and pyarrow.

    This function supports both chunked and non-chunked processing. For large files,
    use chunked processing by specifying input_chunk_size. The function automatically
    detects formats from file extensions if not specified.

    Args:
        input_file: Path to the input file
        output_file: Path to the output file
        input_format: Input format (auto-detected if None)
        output_format: Output format (auto-detected if None)
        compression: Compression type for output (e.g., "gzip", "snappy")
        compression_level: Compression level (1-9 for gzip)
        rows: Row selection in format "start:end" (e.g., "0:100")
        sheet_name: Sheet name for Excel files
        table_number: Table number for HTML files (0-indexed)
        sas_keep_bytes: Keep SAS data as bytes instead of converting to UTF-8
        input_chunk_size: Size of chunks for reading (enables chunked processing)
        output_chunk_size: Size of chunks for writing (currently unused)
        schema_file: Optional JSON file specifying schema to use for reading/writing
        config: Additional configuration (currently unused)

    Raises:
        NotImplementedError: If chunking is not supported for the specified formats
        ValueError: If input or output format is not supported
        FileNotFoundError: If input file or schema file doesn't exist
        Exception: For other conversion errors

    Example:
        >>> convert_data("data.csv", "data.parquet", compression="snappy")
        >>> convert_data("large.csv", "large.parquet", input_chunk_size=10000)
        >>> convert_data("data.xlsx", "data.csv", sheet_name="Sheet1", rows="0:100")
    """
    try:
        # Determine formats and encoding
        in_fmt = infer_format(input_file, input_format)
        out_fmt = infer_format(output_file, output_format)
        sas_encoding = None if sas_keep_bytes else "utf-8"

        # Load schema if provided
        user_schema = None
        if schema_file:
            user_schema = _load_schema(schema_file)

        # Validate chunking support
        _validate_chunking_support(in_fmt, out_fmt, input_chunk_size, output_chunk_size)

        # Handle chunked conversion
        if input_chunk_size:
            _handle_chunked_conversion(
                input_file, output_file, in_fmt, out_fmt, input_chunk_size, sas_encoding
            )
            return

        # Non-chunked conversion
        read_kwargs = _build_read_kwargs(in_fmt, sheet_name, table_number)
        df = _read_dataframe(
            input_file, in_fmt, read_kwargs, sas_encoding, table_number, user_schema
        )

        # Process dataframe
        df = _apply_row_selection(df, rows)
        df = _convert_dtypes(df)

        # Write dataframe
        write_kwargs = _build_write_kwargs(
            compression, compression_level, sheet_name, out_fmt
        )
        _write_dataframe(df, output_file, out_fmt, write_kwargs)

    except Exception as e:
        console.print(f"[bold red]Conversion failed:[/bold red] {e}")
        if "df" in locals():
            _show_preview(df, msg="Partial data preview (error context)")
        raise


def _get_schema_from_arrow_format(input_file: str, input_format: str):
    """Get schema from Arrow-based formats (parquet, feather).

    Args:
        input_file: Path to the input file
        input_format: The input file format ("parquet" or "feather")

    Returns:
        pyarrow.Schema: The schema from the Arrow file
    """
    import pyarrow as pa

    if input_format == "feather":
        table = pa.ipc.open_file(input_file)
    else:  # parquet
        table = pa.parquet.read_table(input_file)
    return table.schema


def _get_schema_from_pandas_format(
    input_file: str,
    input_format: str,
    read_kwargs: Dict,
    sas_encoding: Optional[str],
    table_number: Optional[int],
    schema: Optional[object] = None,
):
    """Get schema from pandas-based formats.

    Args:
        input_file: Path to the input file
        input_format: The input file format
        read_kwargs: Dictionary of read parameters
        sas_encoding: Encoding for SAS files
        table_number: Table number for HTML files
        schema: Optional PyArrow schema to use for reading

    Returns:
        pyarrow.Schema: The inferred schema from the pandas dataframe
    """
    import pyarrow as pa

    df = _read_dataframe(
        input_file, input_format, read_kwargs, sas_encoding, table_number, schema
    )
    return pa.Schema.from_pandas(df)


def _export_schema_to_json(schema, output_file: str):
    """Export schema to JSON file.

    Args:
        schema: The pyarrow schema to export
        output_file: Path to the output JSON file

    Raises:
        IOError: If the file cannot be written
    """
    schema_json = {"fields": [{"name": f.name, "type": str(f.type)} for f in schema]}
    with open(output_file, "w") as f:
        json.dump(schema_json, f, indent=2)


def infer_and_export_schema(
    input_file: str,
    input_format: Optional[str],
    output_file: str,
    nrows: int = 10000,
    sheet_name: Optional[str] = None,
    table_number: Optional[int] = None,
    sas_keep_bytes: bool = False,
):
    """Infer schema from input file and export as JSON.

    This function reads a sample of the input file to infer the data schema
    and exports it as a JSON file. For large files, it only reads the first
    nrows to speed up schema inference.

    Args:
        input_file: Path to the input file
        input_format: Input format (auto-detected if None)
        output_file: Path to the output JSON schema file
        nrows: Number of rows to read for schema inference (default: 10000)
        sheet_name: Sheet name for Excel files
        table_number: Table number for HTML files (0-indexed)
        sas_keep_bytes: Keep SAS data as bytes instead of converting to UTF-8

    Raises:
        ValueError: If input format is not supported
        FileNotFoundError: If input file doesn't exist
        IOError: If output file cannot be written

    Example:
        >>> infer_and_export_schema("data.csv", None, "schema.json")
        >>> infer_and_export_schema("data.xlsx", None, "schema.json", sheet_name="Sheet1")
    """
    in_fmt = infer_format(input_file, input_format)
    sas_encoding = None if sas_keep_bytes else "utf-8"

    # Handle Arrow-based formats
    if in_fmt in {"parquet", "feather"}:
        schema = _get_schema_from_arrow_format(input_file, in_fmt)
    else:
        # Handle pandas-based formats
        read_kwargs = {}
        if in_fmt == "csv":
            read_kwargs["nrows"] = nrows
        elif in_fmt in ["excel", "xlsx"] and sheet_name:
            read_kwargs["sheet_name"] = sheet_name
        elif in_fmt == "html" and table_number is not None:
            read_kwargs["match"] = None
            read_kwargs["flavor"] = "bs4"
            read_kwargs["header"] = 0
            read_kwargs["index_col"] = None

        schema = _get_schema_from_pandas_format(
            input_file, in_fmt, read_kwargs, sas_encoding, table_number
        )

    # Export schema to JSON
    _export_schema_to_json(schema, output_file)
