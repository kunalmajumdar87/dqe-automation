import argparse
import json
import random
import string
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType


try:
    from ydata_profiling import ProfileReport
except Exception:  # pragma: no cover
    ProfileReport = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Task 1 and Task 2 PySpark solution")
    parser.add_argument("--sales-path", required=True, help="Path to sales.csv")
    parser.add_argument("--sellers-path", required=True, help="Path to sellers.csv")
    parser.add_argument(
        "--output-dir",
        default="generated_report",
        help="Output directory for reports and artifacts",
    )
    return parser.parse_args()


def build_spark() -> SparkSession:
    return SparkSession.builder.appName("Task1_Task2_PySpark").getOrCreate()


def build_not_matched_schema_df(spark: SparkSession, expected_schema: StructType, actual_schema: StructType):
    expected_map = {f.name: (f.dataType.simpleString(), f.nullable) for f in expected_schema.fields}
    actual_map = {f.name: (f.dataType.simpleString(), f.nullable) for f in actual_schema.fields}

    all_columns = sorted(set(expected_map.keys()).union(actual_map.keys()))
    rows = []
    for col_name in all_columns:
        exp = expected_map.get(col_name)
        act = actual_map.get(col_name)
        if exp == act:
            continue

        if exp is None:
            rows.append((col_name, "missing_in_expected", None, act[0], None, act[1]))
        elif act is None:
            rows.append((col_name, "missing_in_actual", exp[0], None, exp[1], None))
        else:
            rows.append((col_name, "type_or_nullable_mismatch", exp[0], act[0], exp[1], act[1]))

    schema = StructType(
        [
            StructField("column_name", StringType(), False),
            StructField("mismatch_type", StringType(), False),
            StructField("expected_type", StringType(), True),
            StructField("actual_type", StringType(), True),
            StructField("expected_nullable", StringType(), True),
            StructField("actual_nullable", StringType(), True),
        ]
    )

    string_rows = [
        (
            r[0],
            r[1],
            r[2],
            r[3],
            None if r[4] is None else str(r[4]),
            None if r[5] is None else str(r[5]),
        )
        for r in rows
    ]
    return spark.createDataFrame(string_rows, schema)


def task_1(spark: SparkSession, sales_path: str, output_dir: Path):
    sales_df = spark.read.csv(sales_path, header=True, inferSchema=True)

    # 1) Filter seller_id = 2
    sales_df_seller_2 = sales_df.filter(F.col("seller_id") == 2)

    # 2) ydata-profiling report generation in HTML + JSON
    if ProfileReport is None:
        raise ImportError("ydata-profiling is not installed in the current environment")

    seller2_pdf = sales_df_seller_2.toPandas()
    profile = ProfileReport(seller2_pdf, title="sales_df_seller_2 profiling", explorative=True)

    html_report_path = output_dir / "sales_df_seller_2_profile.html"
    json_report_path = output_dir / "sales_df_seller_2_profile.json"

    profile.to_file(html_report_path.as_posix())
    with json_report_path.open("w", encoding="utf-8") as f:
        f.write(profile.to_json())

    # 3) Mask num_pieces_sold values
    sales_df_seller_2_masked = sales_df_seller_2.withColumn("num_pieces_sold", F.lit("---"))

    # 4) Reformat date to DD.MM.YYYY and validate format with regexp_extract + when
    regex_date = r"^\\d{2}\\.\\d{2}\\.\\d{4}$"
    sales_df_seller_2_date_checked = (
        sales_df_seller_2_masked.withColumn(
            "date",
            F.date_format(F.to_date(F.col("date")), "dd.MM.yyyy"),
        )
        .withColumn("regex_extract_result", F.regexp_extract(F.col("date"), regex_date, 0))
        .withColumn(
            "is_match_regex",
            F.when(F.col("regex_extract_result") != "", F.lit(True)).otherwise(F.lit(False)),
        )
        .drop("regex_extract_result")
    )

    # 5) Expected schema + warehouseId; add department to actual; compare and keep only not matched
    expected_schema = StructType(sales_df.schema.fields + [StructField("warehouseId", IntegerType(), True)])

    sales_df_seller_2_with_department = sales_df_seller_2_date_checked.withColumn("department", F.lit("test"))

    not_matched_schema_df = build_not_matched_schema_df(
        spark=spark,
        expected_schema=expected_schema,
        actual_schema=sales_df_seller_2_with_department.schema,
    )

    print("Task 1 completed")
    print(f"sales_df count: {sales_df.count()}")
    print(f"sales_df_seller_2 count: {sales_df_seller_2.count()}")
    print(f"HTML profile report: {html_report_path}")
    print(f"JSON profile report: {json_report_path}")
    print("Not matched schema fields:")
    not_matched_schema_df.show(truncate=False)

    return {
        "sales_df": sales_df,
        "sales_df_seller_2": sales_df_seller_2,
        "sales_df_seller_2_masked": sales_df_seller_2_masked,
        "sales_df_seller_2_date_checked": sales_df_seller_2_date_checked,
        "sales_df_seller_2_with_department": sales_df_seller_2_with_department,
        "expected_schema": expected_schema,
        "not_matched_schema_df": not_matched_schema_df,
    }


def task_2(spark: SparkSession, sellers_path: str):
    sellers_df = spark.read.csv(sellers_path, header=True, inferSchema=True)

    seller_id_int = F.col("seller_id").cast("int")

    # 2) Update specific rows using transformations
    sellers_updated_df = (
        sellers_df.withColumn(
            "seller_name",
            F.when(seller_id_int == 3, F.lit("n/a"))
            .when(seller_id_int == 6, F.lit(None).cast("string"))
            .when(seller_id_int == 7, F.lit("NULL"))
            .otherwise(F.col("seller_name")),
        )
        .withColumn(
            "daily_target",
            F.when(seller_id_int == 3, F.lit("Undefined"))
            .when(seller_id_int == 6, F.lit("None"))
            .when(seller_id_int == 7, F.lit("61878"))
            .otherwise(F.col("daily_target").cast("string")),
        )
    )

    # Null count per column
    null_count_exprs = [
        F.sum(F.when(F.col(c).isNull(), F.lit(1)).otherwise(F.lit(0))).alias(c)
        for c in sellers_updated_df.columns
    ]
    null_counts_df = sellers_updated_df.agg(*null_count_exprs)

    # 3) UDF to generate random SSN values
    @F.udf(returnType=StringType())
    def generate_random_ssn() -> str:
        digits = "".join(random.choices(string.digits, k=9))
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"

    sellers_with_ssn_df = sellers_updated_df.withColumn("SSN", generate_random_ssn())

    # 4) UDF to mask SSN except first and last characters
    @F.udf(returnType=StringType())
    def mask_ssn(ssn: str):
        if ssn is None:
            return None
        if len(ssn) <= 2:
            return ssn
        return ssn[0] + ("*" * (len(ssn) - 2)) + ssn[-1]

    sellers_masked_ssn_df = sellers_with_ssn_df.withColumn("masked_SSN", mask_ssn(F.col("SSN"))).drop("SSN")

    print("Task 2 completed")
    print("Updated rows for seller_id in (3, 6, 7):")
    sellers_updated_df.filter(seller_id_int.isin([3, 6, 7])).show(truncate=False)
    print("Null counts per column:")
    null_counts_df.show(truncate=False)
    print("Dataframe with masked SSN (original SSN removed):")
    sellers_masked_ssn_df.show(5, truncate=False)

    return {
        "sellers_df": sellers_df,
        "sellers_updated_df": sellers_updated_df,
        "null_counts_df": null_counts_df,
        "sellers_with_ssn_df": sellers_with_ssn_df,
        "sellers_masked_ssn_df": sellers_masked_ssn_df,
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    try:
        task_1_result = task_1(spark, args.sales_path, output_dir)
        task_2_result = task_2(spark, args.sellers_path)

        # Save minimal execution metadata for quick verification.
        metadata = {
            "task1_rows_seller_2": task_1_result["sales_df_seller_2"].count(),
            "task2_rows": task_2_result["sellers_df"].count(),
            "output_dir": str(output_dir.resolve()),
        }
        metadata_path = output_dir / "task1_task2_execution_metadata.json"
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"Execution metadata saved to: {metadata_path}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
