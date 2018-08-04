import csv
import re
from datetime import datetime
from pprint import pprint
from glob import glob
from collections import namedtuple, defaultdict

from tabulate import tabulate



#class TimeRange:
#    """
#    TimeRange('2018-07-01 10:46:27', '2018-07-01 13:16:17')
#    """
#    def __init__(self, start, end):
#        self.start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
#        self.end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
#        self.timedelta = self.end - self.start
#
#    def __repr__(self):
#        return f"TimeRange({self.start}, {self.end})"
#
#
#def merge_calls(calls):
#    ranges = []
#    for call in calls:
#        ranges.append(TimeRange(call.start_time, call.end_time))
#    print(ranges)


class Caller:
    def __init__(self, fcc_caller_str):
        if '-' in fcc_caller_str:
            self.email, self.name = fcc_caller_str.split(' - ')
        else:
            self.email, self.name = '', fcc_caller_str

    def __repr__(self):
        return (self.__class__.__qualname__ +
                f"(name={self.name}, email={self.email})")

    def __hash__(self):
        return hash((self.email, self.name))



def convert_timestamp(timestamp):
    regex = re.compile(r'([0-9\-]+\s+[0-9:]+)\s')
    return regex.search(timestamp).group(1)


def parse_csv_to_list_of_records(filename):
    Record = namedtuple('Record',
                        'caller service_type start_time end_time duration')
    with open(filename) as f:
        all_records = [Record(*row) for row in csv.reader(f)]
    return all_records


def organise_records_by_caller(records):
    voip_calls_dict = defaultdict(list)
    for record in records:
        if record.service_type == 'VoIP':
            record = record._replace(
                start_time=convert_timestamp(record.start_time),
                end_time=convert_timestamp(record.end_time))
            voip_calls_dict[record.caller].append(record)
    return voip_calls_dict


def merge_calls_to_single_record(calls):
    CallSummary = namedtuple('CallSummary',
                             'first_seen last_seen duration')
    sorted_calls = sorted(calls)
    total_duration = 0
    first_seen = sorted_calls[0].start_time
    for call in sorted_calls:
        total_duration += int(call.duration.strip('m'))
    last_seen = call.end_time
    return CallSummary(first_seen, last_seen, total_duration)


def csv_to_record_dict(csv_file):
    records_list = parse_csv_to_list_of_records(csv_file)
    records_dict = organise_records_by_caller(records_list)

    merged_dict = {}
    for caller_str, calls in records_dict.items():
        merged_dict[Caller(caller_str)] = merge_calls_to_single_record(calls)
    return merged_dict


def lecture_stats(csv_file):
    records_dict = csv_to_record_dict(csv_file)

    sorted_by_duration = sorted(
        records_dict.items(), reverse=True, key=lambda x: x[1].duration)
    return sorted_by_duration


def pprint_lecture_report(stats):
    for caller, call in stats:
        print('{:20} {:40} {}'.format(caller.name, caller.email, call.duration))



if __name__ == "__main__":
    #csv_file = 'fcc_csv_data/Conference_173035710_01_07.csv'
    csv_file = 'Conference_test_data.csv'

    pprint_lecture_report(lecture_stats(csv_file))

