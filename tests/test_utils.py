def test_infer_format():
    from src.daflip.utils import infer_format

    assert infer_format("file.csv") == "csv"
    assert infer_format("file.tsv") == "tsv"
    assert infer_format("file.txt", override="fixed") == "fixed"
