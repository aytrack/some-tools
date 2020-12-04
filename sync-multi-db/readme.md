# 使用方法
1. 将 `sync-diff-inspector` 的可执行文件放在该目录下
2. 修改原始配置文件`sync-config.toml`，配置 resource-db 和 target-db:
    ```
    [[source-db]]
        host = "172.16.200.116"
        port = 5000
        user = "root"
        password = ""
        # The instance ID of the source database, the unique identifier of a database instance
        instance-id = "source-1"
        # Uses the snapshot function of TiDB.
        # If enabled, the history data is used for comparison.
        # snapshot = "2016-10-08 16:45:26"
        # Sets the `sql-mode` of the database to parse table structures.
        # sql-mode = ""

    # Configuration of the target database instance
    [target-db]
        host = "192.168.100.1"
        port = 5001
        user = "root"
        password = ""
        # Uses the snapshot function of TiDB.
        # If enabled, the history data is used for comparison.
    ```
3. 修改 `sync-multi-db.py` 中要忽略的 schema
    ```
    ignore_tables = ["INFORMATION_SCHEMA", "mysql", "METRICS_SCHEMA", "PERFORMANCE_SCHEMA", "drainer185_2", "drainer86_1"]
    ```
4. 执行`sync-multi-db.py` 文件 
