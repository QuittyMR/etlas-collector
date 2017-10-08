from typing import List

from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.pool import NullPool

from platforms.helpers.dataframes import DataframeUtils


class MysqlConnection(object):
    """
    Usage: Instantiate this class in a 'with' statement to create an auto-closing, non-managed connection.
    Contains helper functions pertaining to table reflection and loading of data dataframes (see public methods)
    """
    def __init__(self, username: str, password: str, hostname: str, db: str, table: str = None) -> None:
        super(MysqlConnection, self).__init__()
        self._table = table
        self._connection_string = f'mysql+mysqldb://{username}:{password}@{hostname}/{db}'

    def __enter__(self):
        self._connection = create_engine(self._connection_string, poolclass=NullPool)
        self._connection.begin(close_with_result=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.dispose()

    def execute(self, *args, **kwargs):
        return self._connection.execute(*args, **kwargs)

    def store(self, data, updater, table=None) -> str:
        """
        Aggregates data according to the table's unique constraint, drops all redundant columns and stores stores in DB.
        The DB reflection makes this process generic.
        :type table: str
        :type data: pandas.DataFrame
        :param updater: any method used to log messages
        """
        if not table:
            table = self._table

        db_data = self.get_table_metadata(table)
        updater('storage', 'analyzed table')

        data.drop(list(filter(lambda column: column not in db_data['columns'], data.columns)), axis=1, inplace=True)
        data = data.groupby(db_data['unique'], as_index=False, sort=False).sum(index=1, numeric_only=True)
        updater('processed', data.to_csv())

        updater('storage', 'loading into MySQL')
        result = self._insert_records(table, DataframeUtils.to_records(data))
        return 'wrote ids {start} through {finish}'.format(
            start=str(result.lastrowid - result.rowcount),
            finish=str(result.lastrowid)
        )

    def get_table_metadata(self, table: str = None) -> dict:
        # TODO: Make sure this doesn't get called twice
        if not table:
            table = self._table
        return {
            'columns': self._get_columns(table=table),
            'unique': self._get_unique_constraint(table=table)
        }

    def _get_unique_constraint(self, table: str) -> list:
        query = f'show indexes from {table} WHERE non_unique = 0 and Key_name != "PRIMARY";'
        return [column.Column_name for column in self._connection.execute(query).fetchall()]

    def _get_columns(self, table: str) -> list:
        db = self._connection.url.database
        query = f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="{db}" AND TABLE_NAME="{table}"'
        return [column[0] for column in self._connection.execute(query).fetchall()]

    def _insert_records(self, table: str, records: List[dict]):
        """
        Safely inserts records by creating a dynamic table instance
        """
        columns = [Column(column_name) for column_name in self._get_columns(table)]
        table = Table(table, MetaData(), *columns)
        insert_query = insert(table, values=records)
        insert_query = insert_query.on_duplicate_key_update(**insert_query.values)

        return self._connection.execute(insert_query)
