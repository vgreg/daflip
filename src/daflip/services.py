"""
Data conversion services.
"""

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


def _show_preview(df: pd.DataFrame, msg: str = "Data preview"):
    table = Table(title=msg)
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.head(5).iterrows():
        table.add_row(*[str(x) for x in row])
    console.print(table)


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

    Args:
        schema_file: Optional JSON file specifying schema to use for reading/writing.
    """
    import json

    import pyarrow as pa

    try:
        in_fmt = infer_format(input_file, input_format)
        out_fmt = infer_format(output_file, output_format)
        sas_encoding = None if sas_keep_bytes else "utf-8"
        user_schema = None
        if schema_file:
            with open(schema_file, "r") as f:
                schema_json = json.load(f)
                user_schema = pa.schema(
                    [
                        pa.field(f["name"], getattr(pa, f["type"]))
                        for f in schema_json["fields"]
                    ]
                )
        # Supported chunked reading
        chunked_read_formats = {"csv", "sas7bdat"}
        chunked_write_formats = {"csv", "parquet"}  # feather does not support append
        # Validate chunking support
        if input_chunk_size and in_fmt not in chunked_read_formats:
            raise NotImplementedError(
                f"Chunked reading is not supported for input format: {in_fmt}"
            )
        if output_chunk_size and out_fmt not in chunked_write_formats:
            raise NotImplementedError(
                f"Chunked writing is not supported for output format: {out_fmt}"
            )
        # Read in chunks if requested
        if input_chunk_size:
            if in_fmt == "csv":
                reader = pd.read_csv(
                    input_file, chunksize=input_chunk_size, dtype_backend="pyarrow"
                )
            elif in_fmt == "sas7bdat":
                reader = pd.read_sas(
                    input_file, chunksize=input_chunk_size, encoding=sas_encoding
                )
            else:
                raise NotImplementedError(
                    f"Chunked reading is not implemented for {in_fmt}"
                )
            first = True
            for chunk in reader:
                # Row selection not supported in chunked mode
                # Write chunk
                if out_fmt == "csv":
                    chunk.to_csv(
                        output_file,
                        mode="w" if first else "a",
                        header=first,
                        index=False,
                    )
                elif out_fmt == "parquet":
                    import pyarrow as pa
                    import pyarrow.parquet as pq

                    table = pa.Table.from_pandas(chunk)
                    if first:
                        pqwriter = pq.ParquetWriter(output_file, table.schema)
                    pqwriter.write_table(table)
                first = False
            if out_fmt == "parquet" and "pqwriter" in locals():
                pqwriter.close()
            return
        # Non-chunked read
        read_kwargs = {"dtype_backend": "pyarrow"}
        if in_fmt in SEP_MAP:
            read_kwargs["sep"] = SEP_MAP[in_fmt]
        if in_fmt == "fixed":
            raise NotImplementedError(
                "Fixed-width file support is not yet implemented."
            )
        if in_fmt == "excel" and sheet_name:
            read_kwargs["sheet_name"] = sheet_name
        if in_fmt == "html" and table_number is not None:
            read_kwargs["match"] = None
            read_kwargs["flavor"] = "bs4"
            read_kwargs["header"] = 0
            read_kwargs["index_col"] = None
        # Read file
        if in_fmt == "csv" or in_fmt in SEP_MAP:
            df = pd.read_csv(input_file, **read_kwargs)
        elif in_fmt == "parquet":
            df = pd.read_parquet(input_file, **read_kwargs)
        elif in_fmt == "orc":
            df = pd.read_orc(input_file, **read_kwargs)
        elif in_fmt == "feather":
            df = pd.read_feather(input_file, **read_kwargs)
        elif in_fmt == "sas7bdat":
            df = pd.read_sas(input_file, encoding=sas_encoding)
        elif in_fmt == "stata":
            df = pd.read_stata(input_file)
        elif in_fmt == "spss":
            df = pd.read_spss(input_file)
        elif in_fmt == "excel":
            df = pd.read_excel(input_file, **read_kwargs)
        elif in_fmt == "html":
            dfs = pd.read_html(input_file, **read_kwargs)
            if table_number is not None and 0 <= table_number < len(dfs):
                df = dfs[table_number]
            else:
                df = dfs[0]
        else:
            raise ValueError(f"Unsupported input format: {in_fmt}")
        # Row selection
        if rows:
            try:
                start, end = map(int, rows.split(":"))
                df = df.iloc[start:end]
            except Exception:
                console.print(
                    f"[yellow]Warning: Could not parse rows '{rows}', ignoring row selection."
                )
        # Convert dtypes to pyarrow if not already (skip if already done for SAS)
        if hasattr(df, "convert_dtypes"):
            df = df.convert_dtypes(dtype_backend="pyarrow")
        # Write
        write_kwargs = {}
        if compression:
            write_kwargs["compression"] = compression
        if compression_level is not None:
            write_kwargs["compression_level"] = compression_level
        if out_fmt == "csv":
            write_kwargs["sep"] = ","
            df.to_csv(output_file, index=False, **write_kwargs)
        elif out_fmt == "parquet":
            df.to_parquet(output_file, index=False, **write_kwargs)
        elif out_fmt == "orc":
            df.to_orc(output_file, index=False, **write_kwargs)
        elif out_fmt == "feather":
            df.to_feather(output_file, index=False, **write_kwargs)
        elif out_fmt == "excel":
            if sheet_name:
                write_kwargs["sheet_name"] = sheet_name
            df.to_excel(output_file, index=False, **write_kwargs)
        elif out_fmt == "stata":
            df.to_stata(output_file, index=False, **write_kwargs)
        else:
            raise ValueError(f"Unsupported output format: {out_fmt}")
    except Exception as e:
        console.print(f"[bold red]Conversion failed:[/bold red] {e}")
        if "df" in locals():
            _show_preview(df, msg="Partial data preview (error context)")
        raise


def infer_and_export_schema(
    input_file: str,
    input_format: Optional[str],
    output_file: str,
    nrows: int = 10000,
    sheet_name: Optional[str] = None,
    table_number: Optional[int] = None,
    sas_keep_bytes: bool = False,
):
    """Infer schema from input file and export as JSON."""
    import json

    import pandas as pd
    import pyarrow as pa

    from .utils import infer_format

    in_fmt = infer_format(input_file, input_format)
    schema = None
    sas_encoding = None if sas_keep_bytes else "utf-8"
    if in_fmt in {"parquet", "feather"}:
        table = (
            pa.ipc.open_file(input_file)
            if in_fmt == "feather"
            else pa.parquet.read_table(input_file)
        )
        schema = table.schema
    else:
        read_kwargs = {}
        if in_fmt == "csv":
            read_kwargs["nrows"] = nrows
        elif in_fmt == "excel" and sheet_name:
            read_kwargs["sheet_name"] = sheet_name
        elif in_fmt == "html" and table_number is not None:
            read_kwargs["match"] = None
            read_kwargs["flavor"] = "bs4"
            read_kwargs["header"] = 0
            read_kwargs["index_col"] = None
        if in_fmt == "csv":
            df = pd.read_csv(input_file, **read_kwargs)
        elif in_fmt == "orc":
            df = pd.read_orc(input_file)
        elif in_fmt == "sas7bdat":
            df = pd.read_sas(
                input_file, chunksize=nrows, encoding=sas_encoding
            ).__next__()
        elif in_fmt == "stata":
            df = pd.read_stata(input_file)
        elif in_fmt == "spss":
            df = pd.read_spss(input_file)
        elif in_fmt == "excel":
            df = pd.read_excel(input_file, **read_kwargs)
        elif in_fmt == "html":
            dfs = pd.read_html(input_file, **read_kwargs)
            if table_number is not None and 0 <= table_number < len(dfs):
                df = dfs[table_number]
            else:
                df = dfs[0]
        else:
            raise ValueError(f"Unsupported input format: {in_fmt}")
        schema = pa.Schema.from_pandas(df)
    # Export schema to JSON
    schema_json = {"fields": [{"name": f.name, "type": str(f.type)} for f in schema]}
    with open(output_file, "w") as f:
        json.dump(schema_json, f, indent=2)
