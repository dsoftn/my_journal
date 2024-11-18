from typing import Union, Any
from datetime import datetime
from datetime import timedelta

from utils_log import LogHandler
import settings_cls


class Period:
    def __init__(
            self,
            total_seconds: Union[int, float, timedelta] = 0,
            convert_to_positive_value: bool = False
            ) -> None:

        if isinstance(total_seconds, timedelta):
            self.__total_seconds = int(total_seconds.total_seconds())
        elif isinstance(total_seconds, int):
            self.__total_seconds = total_seconds
        elif isinstance(total_seconds, float):
            self.__total_seconds = int(total_seconds)
        else:
            LogHandler.add_log_record("#1: Cannot initialize #1 object with #2.\nType of #3 must be #4, #5 or #6.", ["Period", type(total_seconds), "total_seconds", "Int", "Float", "timedelta"], exception_raised=True)
            raise ValueError(f"Cannot initialize Period object with total_seconds of type {type(total_seconds)}!")
    
        if convert_to_positive_value:
            self.__total_seconds = abs(self.__total_seconds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.total_seconds == other.total_seconds

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.total_seconds > other.total_seconds

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.total_seconds < other.total_seconds

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.total_seconds >= other.total_seconds

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.total_seconds <= other.total_seconds

    def __str__(self) -> str:
        return f"Period: {self.years} years, {self.months} months, {self.days} days, {self.hours} hours, {self.minutes} minutes and {self.seconds} seconds."
    
    def __sub__(self, other: object) -> 'Period':
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot subtract #1 object from #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot subtract objects of different types!")
        
        return Period(self.total_seconds - other.total_seconds)

    def __add__(self, other: object) -> 'Period':
        if not isinstance(other, Period):
            LogHandler.add_log_record("#1: Cannot subtract #1 object from #2.\nObjects must be same type.", ["Period", type(other)], exception_raised=True)
            raise ValueError("Cannot subtract objects of different types!")
        
        return Period(self.total_seconds + other.total_seconds)

    def set_period(
            self,
            years: int = 0,
            months: int = 0,
            days: int = 0,
            hours: int = 0,
            minutes: int = 0,
            seconds: int = 0
    ):
        total_sec = seconds
        total_sec += minutes * 60
        total_sec += hours * 60 * 60
        total_sec += days * 60 * 60 * 24
        total_sec += months * 60 * 60 * 24 * 30
        total_sec += years * 60 * 60 * 24 * 30 * 12

        self.__total_seconds = total_sec

    @property
    def total_years(self) -> int:
        return int(self.__total_seconds / (60 * 60 * 24 * 30 * 12))

    @property
    def total_months(self) -> int:
        return int(self.__total_seconds / (60 * 60 * 24 * 30))
    
    @property
    def total_days(self) -> int:
        return int(self.__total_seconds / (60 * 60 * 24))
    
    @property
    def total_hours(self) -> int:
        return int(self.__total_seconds / (60 * 60))
    
    @property
    def total_minutes(self) -> int:
        return int(self.__total_seconds / 60)
    
    @property
    def total_seconds(self) -> int:
        return int(self.__total_seconds)
    
    @property
    def years(self) -> int:
        return int(self.__total_seconds / (60 * 60 * 24 * 30 * 12))
    
    @property
    def months(self) -> int:
        return (int(self.__total_seconds / (60 * 60 * 24 * 30)) % 12)

    @property
    def days(self) -> int:
        return (int(self.__total_seconds / (60 * 60 * 24)) % 30)
    
    @property
    def hours(self) -> int:
        return (int(self.__total_seconds / (60 * 60)) % 24)
    
    @property
    def minutes(self) -> int:
        return (int(self.__total_seconds / 60) % 60)
    
    @property
    def seconds(self) -> int:
        return int(self.__total_seconds % 60)


class DateTimeObject:
    def __init__(self, datetime_object: Union[datetime, str, 'DateTimeObject', float], **kwargs):
        from utils_settings import UTILS_Settings
        
        self.date_format = UTILS_Settings.DATE_FORMAT if kwargs.get("date_format") is None else kwargs.get("date_format")
        self.time_format = UTILS_Settings.TIME_FORMAT if kwargs.get("time_format") is None else kwargs.get("time_format")
        self.datetime_format_delimiter = UTILS_Settings.DATE_TIME_FORMAT_DELIMITER if kwargs.get("datetime_format_delimiter") is None else kwargs.get("datetime_format_delimiter")

        self.datetime_object: datetime = self._fix_datetime_object(datetime_object, date_format=self.date_format, time_format=self.time_format, datetime_delimiter=self.datetime_format_delimiter)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DateTimeObject):
            return False

        return self.datetime_object == other.datetime_object

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, DateTimeObject):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["DateTimeObject", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.datetime_object > other.datetime_object

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, DateTimeObject):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["DateTimeObject", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.datetime_object < other.datetime_object

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, DateTimeObject):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["DateTimeObject", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.datetime_object >= other.datetime_object

    def __le__(self, other: object) -> bool:
        if not isinstance(other, DateTimeObject):
            LogHandler.add_log_record("#1: Cannot compare #1 object with #2.\nObjects must be same type.", ["DateTimeObject", type(other)], exception_raised=True)
            raise ValueError("Cannot compare objects of different types!")

        return self.datetime_object <= other.datetime_object

    def __str__(self) -> str:
        return f"DateTimeObject: {self.DATE_TIME_formatted_string}"
    
    def __sub__(self, other: object) -> Period:
        if not isinstance(other, DateTimeObject):
            LogHandler.add_log_record("#1: Cannot subtract #1 object from #2.\nObjects must be same type.", ["DateTimeObject", type(other)], exception_raised=True)
            raise ValueError("Cannot subtract objects of different types!")
        
        if self.datetime_object == other.datetime_object:
            return Period(0)
        
        diff = self.datetime_object - other.datetime_object
        seconds = diff.total_seconds()

        return Period(seconds)

    def _fix_datetime_object(self, datetime_object: Any, date_format: str = "%d.%m.%Y.", time_format: str = "%H:%M:%S", datetime_delimiter: str = " ", check_is_valid: bool = False) -> datetime:
        if datetime_object is None:
            if check_is_valid:
                return False

            LogHandler.add_log_record("#1: #2 cannot be #3.", ["DateTimeObject", "datetime_object", "None"], exception_raised=True)
            raise ValueError("datetime_object cannot be None!")
        elif isinstance(datetime_object, datetime):
            if check_is_valid:
                return True

            return datetime_object
        elif isinstance(datetime_object, str):
            try:
                result = datetime.strptime(datetime_object, f"{date_format}{datetime_delimiter}{time_format}")
                if check_is_valid:
                    return True

                return result
            except ValueError:
                pass

            try:
                result = datetime.strptime(datetime_object, date_format)
                if check_is_valid:
                    return True

                return result
            except ValueError:
                pass

            try:
                result = datetime.strptime(datetime_object.strip(" ."), date_format.strip(" ."))
                if check_is_valid:
                    return True

                return result
            except ValueError:
                pass

            try:
                tmp_datetime_object = datetime_object
                while True:
                    tmp_datetime_object = tmp_datetime_object.replace("  ", " ")
                    if tmp_datetime_object.find("  ") == -1:
                        break
                result = datetime.strptime(tmp_datetime_object, f"{date_format} {time_format}")
                if check_is_valid:
                    return True

                return result
            except ValueError:
                pass

            try:
                result = datetime.strptime(datetime_object, time_format)
                if check_is_valid:
                    return True

                return result
            except ValueError:
                pass

            if check_is_valid:
                return False
            
            LogHandler.add_log_record("#1: String #2 (#3) does not match format date(#4), time(#5).", ["DateTimeObject", "datetime_object", datetime_object, date_format, time_format], exception_raised=True)
            raise ValueError(f"datetime_object ({datetime_object}) does not match format ({date_format} {time_format})!")
            
        elif isinstance(datetime_object, DateTimeObject):
            if check_is_valid:
                return True
            
            return datetime_object.datetime_object
        elif isinstance(datetime_object, float):
            try:
                result = datetime.fromtimestamp(datetime_object)
                if check_is_valid:
                    return True
                
                return result
            except Exception as e:
                LogHandler.add_log_record("#1: #1 object cannot be created from #2 (#3)\n#4", ["DateTimeObject", "timestamp", datetime_object, str(e)], exception_raised=True)
                raise TypeError(f"datetime_object cannot be created from timestamp {datetime_object}!")
        elif isinstance(datetime_object, int):
            try:
                result = self._date_from_integer(datetime_object)
                if check_is_valid:
                    return True

                return result
            except Exception as e:
                LogHandler.add_log_record("#1: #1 object cannot be created from #2 (#3)\n#4", ["DateTimeObject", "integer", datetime_object, str(e)], exception_raised=True)
                raise TypeError(f"datetime_object cannot be created from integer {datetime_object}!")
        
        LogHandler.add_log_record("#1: Argument #2 type is not supported.\ntype(datetime_object) = #3\ndatetime_object = #4", ["DateTimeObject", "datetime_object", type(datetime_object), datetime_object], exception_raised=True)
        raise TypeError("datetime_object type is not supported!")

    def _date_from_integer(self, integer: int) -> datetime:
        str_integer = str(integer)
        if len(str_integer) != 8:
            LogHandler.add_log_record("#1: #1 object has #2 digits, expected #3. (#4)", ["DateTimeObject", "integer", len(str_integer), 8, integer], warning_raised=True)
            raise TypeError(f"datetime_object cannot be created from integer {integer}, expected 8 digits!")
        
        date = f"{str_integer[6:8]}.{str_integer[4:6]}.{str_integer[0:4]}"

        return datetime.strptime(date, "%d.%m.%Y")
    
    def _get_date_integer(self, date: Union[datetime, str, 'DateTimeObject']):
        date = self._fix_datetime_object(date)
        result = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)

        return int(result)

    def is_valid(self, value: Union[datetime, str, 'DateTimeObject'] = None) -> bool:
        if value is None:
            value = self.datetime_object
        return self._fix_datetime_object(value, check_is_valid=True)

    def date_difference(self, other_DateTimeObject: 'DateTimeObject') -> Period:
        return Period(self.datetime_object - other_DateTimeObject.datetime_object, convert_to_positive_value=True)

    @property
    def DATE_formatted_string(self) -> str:
        return self.datetime_object.strftime(self.date_format)

    @DATE_formatted_string.setter
    def DATE_formatted_string(self, value: str):
        self.datetime_object = self._fix_datetime_object(value)
    
    @property
    def DATE_year(self) -> int:
        return self.datetime_object.year
    
    @DATE_year.setter
    def DATE_year(self, value: int):
        min_val = self.datetime_object.min.year
        max_val = self.datetime_object.max.year

        if value < min_val or value > max_val:
            LogHandler.add_log_record("#1: Value #2 is not a valid year.\nYear must be in range #3 - #4", ["DateTimeObject", value, min_val, max_val], exception_raised=True)
            raise ValueError(f"Value {value} is not a valid year!")
        
        self.datetime_object = self.datetime_object.replace(year=value)

    @property
    def DATE_month(self) -> int:
        return self.datetime_object.month

    @DATE_month.setter
    def DATE_month(self, value: int):
        min_val = self.datetime_object.min.year
        max_val = self.datetime_object.max.year

        if value < min_val or value > max_val:
            LogHandler.add_log_record("#1: Value #2 is not a valid month.\nMonth must be in range #3 - #4", ["DateTimeObject", value, min_val, max_val], exception_raised=True)
            raise ValueError(f"Value {value} is not a valid month!")
        
        self.datetime_object = self.datetime_object.replace(month=value)
    
    @property
    def DATE_day(self) -> int:
        return self.datetime_object.day
    
    @DATE_day.setter
    def DATE_day(self, value: int):
        min_val = self.datetime_object.min.day
        max_val = self.datetime_object.max.day

        if value < min_val or value > max_val:
            LogHandler.add_log_record("#1: Value #2 is not a valid day.\nDay must be in range #3 - #4", ["DateTimeObject", value, min_val, max_val], exception_raised=True)
            raise ValueError(f"Value {value} is not a valid day!")
        
        self.datetime_object = self.datetime_object.replace(day=value)
    
    @property
    def TIME_formatted_string(self) -> str:
        return self.datetime_object.strftime(self.time_format)

    @property
    def TIME_hour(self) -> int:
        return self.datetime_object.hour
    
    @TIME_hour.setter
    def TIME_hour(self, value: int):
        min_val = self.datetime_object.min.hour
        max_val = self.datetime_object.max.hour

        if value < min_val or value > max_val:
            LogHandler.add_log_record("#1: Value #2 is not a valid hour.\nHour must be in range #3 - #4", ["DateTimeObject", value, min_val, max_val], exception_raised=True)
            raise ValueError(f"Value {value} is not a valid hour!")
        
        self.datetime_object = self.datetime_object.replace(hour=value)
    
    @property
    def TIME_minute(self) -> int:
        return self.datetime_object.minute
    
    @TIME_minute.setter
    def TIME_minute(self, value: int):
        min_val = self.datetime_object.min.minute
        max_val = self.datetime_object.max.minute

        if value < min_val or value > max_val:
            LogHandler.add_log_record("#1: Value #2 is not a valid minute.\nMinute must be in range #3 - #4", ["DateTimeObject", value, min_val, max_val], exception_raised=True)
            raise ValueError(f"Value {value} is not a valid minute!")
        
        self.datetime_object = self.datetime_object.replace(minute=value)
    
    @property
    def TIME_second(self) -> int:
        return self.datetime_object.second
    
    @TIME_second.setter
    def TIME_second(self, value: int):
        min_val = self.datetime_object.min.second
        max_val = self.datetime_object.max.second

        if value < min_val or value > max_val:
            LogHandler.add_log_record("#1: Value #2 is not a valid second.\nSecond must be in range #3 - #4", ["DateTimeObject", value, min_val, max_val], exception_raised=True)
            raise ValueError(f"Value {value} is not a valid second!")
        
        self.datetime_object = self.datetime_object.replace(second=value)

    @property
    def DATE_TIME_formatted_string(self) -> str:
        return self.datetime_object.strftime(f"{self.date_format}{self.datetime_format_delimiter}{self.time_format}")
    
    @DATE_TIME_formatted_string.setter
    def DATE_TIME_formatted_string(self, value: str):
        self.datetime_object = self._fix_datetime_object(value)

    @property
    def DayOfWeek(self) -> int:
        return self.datetime_object.weekday()

    @property
    def DateToInteger(self) -> int:
        return self._get_date_integer(self.datetime_object)


class DateTime:
    @staticmethod
    def now() -> DateTimeObject:
        return DateTimeObject(datetime.now())
    
    @staticmethod
    def today() -> DateTimeObject:
        return DateTimeObject(datetime.today())
    
    @staticmethod
    def is_valid(value: Union[DateTimeObject, datetime, str, float, int]) -> DateTimeObject:
        dt_obj = DateTimeObject(DateTime.now())
        return dt_obj.is_valid(value)
    
    @staticmethod
    def get_DateTimeObject(value: Union[DateTimeObject, datetime, str, float, int], **kwargs):
        return DateTimeObject(value, **kwargs)

    @staticmethod
    def get_date_difference(date1: Union[DateTimeObject, datetime, str, float, int], date2: Union[DateTimeObject, datetime, str, float, int]) -> Period:
        dt1 = DateTime.get_DateTimeObject(date1)
        dt2 = DateTime.get_DateTimeObject(date2)
        return dt1.date_difference(dt2)
        
    @staticmethod
    def get_date_integer(date: Union[DateTimeObject, datetime, str, float, int]) -> int:
        dt = DateTime.get_DateTimeObject(date)
        return dt.DateToInteger





