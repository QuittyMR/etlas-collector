from datetime import datetime

import recurrent

from appcore.helpers import errors


class DateConverter(object):
    @staticmethod
    def description_to_date(description: str) -> datetime:
        description = description.replace('back', 'ago').replace('00:00', 'midnight')

        # Forcing all time data to 0 to prevent recurrent from auto-filling with current time
        parsed_date = recurrent.parse(description, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

        if not isinstance(parsed_date, datetime):
            raise errors.FailedParsingDate

        return parsed_date

    @staticmethod
    def description_to_schedule(description: str, is_rfc=False) -> dict:
        if not description:
            return {}

        description = description.replace('back', 'ago')

        schedule = recurrent.RecurringEvent()
        schedule.parse(description)

        if not schedule.is_recurring:
            raise errors.FailedParsingDate
        elif is_rfc:
            return schedule.get_RFC_rrule()
        else:
            return schedule.get_params()
