import matplotlib.pyplot as plt
import psycopg2
import time
import sys

# Подключения к БД
PRIMARY_DB = {
    'dbname':   'postgres',
    'user':     'postgres',
    'password': 'postgres',
    'host':     'localhost',
    'port':     '5433'
}

STANDBY_DB = {
    'dbname':   'postgres',
    'user':     'postgres',
    'password': 'postgres',
    'host':     'localhost',
    'port':     '5434'
}

TABLE = 'data_table'
ITERATIONS = 100
WAIT_TIME = 0.1

class MetricsCollector:
    def __init__(self):
        self.timestamps = []
        self.primary_rows = []
        self.standby_rows = []

    def _row_count(self, db):
        try:
            with psycopg2.connect(**db) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
                    return cur.fetchone()[0]
        except Exception:
            return -1

    def collect(self):
        now = time.time()
        self.timestamps.append(now)
        self.primary_rows.append(self._row_count(PRIMARY_DB))
        self.standby_rows.append(self._row_count(STANDBY_DB))

    def visualize(self):
        if not self.timestamps:
            print("Нет данных для графика.")
            return

        t = [x - self.timestamps[0] for x in self.timestamps]
        print(f"Максимум в primary: {max(self.primary_rows)} / {len(t)} точек")
        print(f"Максимум в standby: {max(self.standby_rows)} / {len(t)} точек")

        plt.figure(figsize=(10, 5))
        plt.plot(t, self.primary_rows, label='Primary', marker='o')
        plt.plot(t, self.standby_rows, label='Standby', linestyle='--')
        plt.title("Количество записей в БД во времени")
        plt.xlabel("Время (сек.)")
        plt.ylabel("Количество записей")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        filename = "picture.png"
        plt.savefig(filename)
        print(f"График сохранён: {filename}")
        plt.show()

class SmartInserter:
    def __init__(self):
        self.use_primary = True

    def switch_to_standby(self):
        try:
            with psycopg2.connect(**STANDBY_DB) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_promote()")
                    conn.commit()
            print("Standby DB успешно повышена до primary.")
        except Exception as e:
            print(f"Ошибка при promote: {e}")

    def _try_insert(self, db, val):
        try:
            with psycopg2.connect(**db) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"INSERT INTO {TABLE}(name) VALUES (%s)", (val,))
                    conn.commit()
            return True
        except Exception:
            return False

    def write(self, val):
        if self.use_primary:
            if not self._try_insert(PRIMARY_DB, val):
                print("Primary недоступна. Переключаемся на standby...")
                self.use_primary = False
                self.switch_to_standby()

        if not self.use_primary:
            self._try_insert(STANDBY_DB, val)

def setup_table():
    with psycopg2.connect(**PRIMARY_DB) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                DROP TABLE IF EXISTS {TABLE};
                CREATE TABLE {TABLE} (
                    id SERIAL PRIMARY KEY,
                    name TEXT
                );
            """)
            conn.commit()
    print(f"Таблица `{TABLE}` готова к работе.")

def generate_data() -> str:
    return "sample_data"

def main():
    inserter = SmartInserter()
    tracker = MetricsCollector()

    setup_table()

    print(f"Стартуем: {ITERATIONS} вставок + сбор метрик (шаг {WAIT_TIME} сек)...")
    try:
        for _ in range(ITERATIONS):
            inserter.write(generate_data())
            tracker.collect()
            time.sleep(WAIT_TIME)
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")

    tracker.visualize()

if __name__ == '__main__':
    main()
