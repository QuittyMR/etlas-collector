from io import BytesIO
from typing import List


class WebUtils(object):
    @classmethod
    def archive_to_records(cls, bytestream: bytes, archive_type: str) -> List[dict]:
        from csv import DictReader
        return list(DictReader(WebUtils._extract_archive(bytestream, archive_type)))

    @classmethod
    def archive_to_dataframe(cls, bytestream: bytes, archive_type: str, data_rows: tuple = (0, -1)):
        """
        :rtype: pandas.DataFrame
        """
        from pandas import read_csv
        from io import StringIO
        data = WebUtils._extract_archive(bytestream, archive_type)
        if data_rows:
            data = '\n'.join(data.splitlines()[data_rows[0]:data_rows[1]])
        return read_csv(StringIO(data))

    @classmethod
    def _extract_gzip(cls, bytestream: bytes) -> str:
        from gzip import decompress
        return decompress(bytestream).decode()

    @classmethod
    def _extract_zip(cls, bytestream: bytes) -> dict:
        from zipfile import ZipFile
        extracted_content = {}
        with ZipFile(BytesIO(bytestream)) as file_handle:
            for item in file_handle.filelist:
                extracted_content[item.filename] = file_handle.read(item).decode()

        return extracted_content

    @classmethod
    def _extract_archive(cls, bytestream: bytes, archive_type: str) -> str:
        """
        Assumes one file in the archive - feel free to modify this behaviour
        """
        if archive_type.lower() == 'zip':
            return WebUtils._extract_zip(bytestream).popitem()[1]
        elif archive_type.lower() in ['gzip', 'gz']:
            return WebUtils._extract_gzip(bytestream)
        else:
            raise NotImplementedError("processing missing for archive type " + archive_type)
