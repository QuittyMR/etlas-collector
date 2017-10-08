class DataframeUtils(object):
    @classmethod
    def to_records(cls, data):
        """
        :type data:pandas.DataFrame
        :rtype: list
        """
        return list(data.T.to_dict().values())
