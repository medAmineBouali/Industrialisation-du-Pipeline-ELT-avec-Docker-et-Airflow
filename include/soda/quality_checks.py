import os
from soda.scan import Scan

def run_soda_checks():
    scan = Scan()
    scan.set_scan_definition_name("youtube_pipeline_checks")
    scan.set_data_source_name("postgres_db_yt_elt")

    scan.add_configuration_yaml_str(f"""
data_source postgres_db_yt_elt:
  type: postgres
  host: {os.environ.get("POSTGRES_CONN_HOST")}
  port: "5432"
  username: {os.environ.get("ELT_DATABASE_USERNAME")}
  password: {os.environ.get("ELT_DATABASE_PASSWORD")}
  database: {os.environ.get("ELT_DATABASE_NAME")}
  schema: public
""")

    scan.add_sodacl_yaml_file(
        file_path="/opt/airflow/include/soda/checks.yml"
    )

    scan.execute()

    if scan.get_error_logs_text():
        raise ValueError(f"Soda checks failed:\n{scan.get_error_logs_text()}")

    print(scan.get_logs_text())
    print("All Soda checks passed.")