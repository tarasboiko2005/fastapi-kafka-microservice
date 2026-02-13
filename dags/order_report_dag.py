from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2

def count_orders():
    conn = psycopg2.connect(
        dsn="postgresql://devuser:devpassword@postgres:5432/devdb"
    )
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM orders;")
    count = cur.fetchone()[0]
    print(f"📊 REPORT: Total orders in database: {count}")
    cur.close()
    conn.close()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_order_report',
    default_args=default_args,
    description='A simple report DAG',
    schedule_interval='@daily',
    start_date=datetime(2026, 2, 13),
    catchup=False,
) as dag:

    report_task = PythonOperator(
        task_id='count_total_orders',
        python_callable=count_orders,
    )