# Copyright (C) 2007-2008 by Bjorn Tillenius

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__metaclass__ = type

import logging
import os
import sys
import time
from datetime import datetime
from optparse import OptionParser

try:
    import xml.etree.ElementTree as ET
except ImportError:
    # For Python 2.4 and earlier.
    import elementtree.ElementTree as ET

import garmin


VERSION = "0.3"

INVALID_CADENCE = 255
INVALID_HEART_RATE = 0
INVALID_POS = (0x7FFFFFFF,)*2
INVALID_TRACK = 65535


def format_date(timestamp):
    value = datetime.utcfromtimestamp(timestamp + garmin.TimeEpoch)
    return value.isoformat() + 'Z'


class GPSInfo:
    """Information about the GPS."""

    def __init__(self, name, version, product_id, unit_id):
        self.name = name
        version_text = "%2.2f" % version
        self.major_version, self.minor_version = version_text.split('.', 1)
        self.product_id = str(product_id)
        self.unit_id = str(unit_id)


class Activity:

    SPORT_TYPES = {
        0: "Running",
        1: "Biking",
        2: "Other",
        }

    def __init__(self, sport):
        assert sport in self.SPORT_TYPES, "Unknown sport: %r" % sport
        self.sport = self.SPORT_TYPES[sport]
        self.laps = []
        self.track = None

    def __repr__(self):
        return "<Activity id=%r sport=%s laps=%s>" % (
            self.id, self.sport, len(self.laps))

    @property
    def id(self):
        first_lap = self.laps[0]
        return format_date(first_lap.start_time)


class ActivityTCXExport:

    def __init__(self, activity, gps_info):
        self.gps_info = gps_info
        self.activity = activity
        self.tcx = ET.Element('TrainingCenterDatabase')
        self.tcx.set(
            'xmlns',
            "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
        self.tcx.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
        self.tcx.set(
            'xsi:schemaLocation',
            "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 "
            "http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")

        self.folders = ET.SubElement(self.tcx, 'Folders')
        self.history = ET.SubElement(self.folders, 'History')
        self.running = ET.SubElement(self.history, 'Running')
        self.running.set('Name', "Running")
        self.biking = ET.SubElement(self.history, 'Biking')
        self.biking.set('Name', "Biking")
        self.other = ET.SubElement(self.history, 'Other')
        self.other.set('Name', "Other")
        self.multisport = ET.SubElement(self.history, 'MultiSport')
        self.multisport.set('Name', "MultiSport")

        self.activities = ET.SubElement(self.tcx, 'Activities')
        self.tcx.append(self.get_author_tag())

    @property
    def filename(self):
        return self.activity.id

    def get_author_tag(self):
        author = ET.Element('Author')
        author.set('xsi:type', 'Application_t')
        name = ET.SubElement(author, 'Name')
        name.text = "Garmin Training Center(TM)"
        build = ET.SubElement(author, "Build")
        
        version = ET.SubElement(build, "Version")
        #major, minor = VERSION.split('.', 1)
        major, minor = '3', '2'
        version_major = ET.SubElement(version, "VersionMajor")
        version_major.text = major
        version_minor = ET.SubElement(version, "VersionMinor")
        version_minor.text = minor
        major_build = ET.SubElement(version, 'BuildMajor')
        major_build.text = "0"
        minor_build = ET.SubElement(version, 'BuildMinor')
        minor_build.text = "5" # original 0
        type_tag = ET.SubElement(build, "Type")
        type_tag.text = "Release"
        time_tag = ET.SubElement(build, 'Time')
        time_tag.text = "Nov 28 2006, 16:55:46"
        builder = ET.SubElement(build, 'Builder')
        builder.text = "SQA"
        lang_id = ET.SubElement(author, "LangID")
        lang_id.text = "EN"
        part_number = ET.SubElement(author, "PartNumber")
        part_number.text = "006-A0119-00"
        return author

    def add_activity(self, activity):
        if activity.sport == "Running":
            sport_folder = self.running
        if activity.sport == "Biking":
            sport_folder = self.biking
        else:
            sport_folder = self.other
        activity_id = ET.Element('Id')
        activity_id.text = activity.id
        activity_ref = ET.SubElement(sport_folder, 'ActivityRef')
        activity_ref.append(activity_id)
        activity_tag = ET.SubElement(self.activities, 'Activity')
        activity_tag.set('Sport', self.activity.sport)
        activity_tag.append(activity_id)
        for lap in activity.laps:
            self.add_lap(activity_tag, lap)
        self.add_creator(activity_tag, self.gps_info)

    def add_creator(self, activity_tag, gps_info):
        """Add a <Creator> tag."""
        creator = ET.SubElement(activity_tag, 'Creator')
        creator.set('xsi:type', 'Device_t')
        name = ET.SubElement(creator, 'Name')
        name.text = gps_info.name
        unit_id = ET.SubElement(creator, 'UnitId')
        #unit_id.text = gps_info.unit_id
        # MP hack
        unit_id.text = "3376710574"
        product = ET.SubElement(creator, 'ProductID')
        #product.text = str(gps_info.product_id)
        product.text = "450"
        version = ET.SubElement(creator, 'Version')
        major_version = ET.SubElement(version, 'VersionMajor')
        major_version.text = '3' #gps_info.major_version
        minor_version = ET.SubElement(version, 'VersionMinor')
        minor_version.text = '20' #gps_info.minor_version
        major_build = ET.SubElement(version, 'BuildMajor')
        major_build.text = "0"
        minor_build = ET.SubElement(version, 'BuildMinor')
        minor_build.text = "0"

    def add_lap(self, activity_tag, lap):
        lap_tag = ET.SubElement(activity_tag, 'Lap')
        lap_tag.set('StartTime', format_date(lap.start_time))
        self.add_float(lap_tag, 'TotalTimeSeconds', lap.total_time/100.0)
        self.add_float(lap_tag, 'DistanceMeters', lap.total_dist)
        self.add_float(lap_tag, 'MaximumSpeed', lap.max_speed)
        self.add_int(lap_tag, 'Calories', lap.calories)
        if lap.avg_heart_rate != INVALID_HEART_RATE:
            self.add_bpm(lap_tag, 'AverageHeartRateBpm', lap.avg_heart_rate)
        if lap.max_heart_rate != INVALID_HEART_RATE:
            self.add_bpm(lap_tag, 'MaximumHeartRateBpm', lap.max_heart_rate)
        self.add_intensity(lap_tag, 'Intensity', lap.intensity)
        if lap.avg_cadence != INVALID_CADENCE:
            self.add_int(lap_tag, 'Cadence', lap.avg_cadence)
        self.add_trigger_method(lap_tag, 'TriggerMethod', lap.trigger_method)
        self.add_tracks(lap_tag, lap, self.activity.track)

    def add_tracks(self, lap_tag, lap, track_points):
        track_tag = ET.SubElement(lap_tag, 'Track')
        previous_trackpoint = None
        lap_distance = 0.0
        # The first track point is the header.
        for track_point in track_points[1:]:
            if track_point.time < lap.start_time:
                continue
            if previous_trackpoint is not None:
                if (self.is_trackpoint_invalid(previous_trackpoint) and
                    self.is_trackpoint_invalid(track_point)):
                    # Two consecutive invalid trackpoints indicate the
                    # beginning of a new track.
                    self.add_track_point(track_tag, previous_trackpoint)
                    track_tag = ET.SubElement(lap_tag, 'Track')
                    self.add_track_point(track_tag, track_point)
                elif (self.is_trackpoint_invalid(previous_trackpoint) or
                      self.is_trackpoint_invalid(track_point)):
                    pass
                else:
                    lap_distance += (
                        track_point.distance - previous_trackpoint.distance)

            if lap_distance >= lap.total_dist:
                break
            if not self.is_trackpoint_invalid(track_point):
                self.add_track_point(track_tag, track_point)
            previous_trackpoint = track_point

    def is_trackpoint_invalid(self, track_point):
        """"Return whether the track point is invalid.

        It's invalid if its postion, altitude and heart rate are invalid.
        """
        return (
            (track_point.slat, track_point.slon) == INVALID_POS and
            track_point.alt > 1.0e24 and
            track_point.heart_rate == INVALID_HEART_RATE)

    def add_track_point(self, track_tag, track_point):
        point_tag = ET.SubElement(track_tag, 'Trackpoint')
        self.add_string(point_tag, 'Time', format_date(track_point.time))
        if self.is_trackpoint_invalid(track_point):
            # An invalid track point should only have a time, nothing else.
            return
        if (track_point.slat, track_point.slon) != INVALID_POS:
            self.add_position(
                point_tag, 'Position', track_point.slat, track_point.slon)
        if track_point.alt < 1.0e24:
            self.add_float(point_tag, 'AltitudeMeters', track_point.alt)
        if track_point.distance < 1.0e24:
            self.add_float(point_tag, 'DistanceMeters', track_point.distance)
        if track_point.heart_rate != INVALID_HEART_RATE:
            self.add_bpm(point_tag, 'HeartRateBpm', track_point.heart_rate)

        # MP
        if track_point.cadence:
            self.add_string(point_tag, 'Cadence', str(int(track_point.cadence)))

        if track_point.sensor:
            self.add_string(point_tag, 'SensorState', 'Present')
        else:
            self.add_string(point_tag, 'SensorState', 'Absent')

    def add_position(self, tag, tag_name, latitude, longitude):
        position_tag = ET.SubElement(tag, tag_name)
        self.add_float(
            position_tag, 'LatitudeDegrees', garmin.degrees(latitude))
        self.add_float(
            position_tag, 'LongitudeDegrees', garmin.degrees(longitude))

    def add_string(self, tag, tag_name, value):
        new_tag = ET.SubElement(tag, tag_name)
        new_tag.text = "%s" % value
        return new_tag

    def add_float(self, tag, tag_name, value):
        new_tag = ET.SubElement(tag, tag_name)
        new_tag.text = "%f" % value
        return new_tag

    def add_int(self, tag, tag_name, value):
        new_tag = ET.SubElement(tag, tag_name)
        new_tag.text = "%i" % value
        return new_tag

    def add_bpm(self, tag, tag_name, value):
        new_tag = ET.SubElement(tag, tag_name)
        new_tag.set('xsi:type', 'HeartRateInBeatsPerMinute_t')
        value_tag = ET.SubElement(new_tag, 'Value')
        value_tag.text = "%i" % value
        return new_tag

    def add_intensity(self, tag, tag_name, value):
        if value == 0:
            intensity = "Active"
        else:
            intensity = "Rest"
        return self.add_string(tag, tag_name, intensity)

    def add_trigger_method(self, tag, tag_name, value):
        if value == 0:
            method = "Manual"
        elif value == 1:
            method = "Distance"
        elif value == 2:
            method = "Location"
        elif value == 3:
            method = "Time"
        elif value == 4:
            method = "Heart Rate"
        else:
            raise AssertionError("Invalid trigger method: %r" % value)
        return self.add_string(tag, tag_name, method)

    def export_to(self, path):
        self.add_activity(self.activity)

        tree = ET.ElementTree(self.tcx)
        tree.write(path)
        return


class ActivityGarmin(garmin.Garmin):
    """A Garmin GPS based around "activites"."""

    def get_activities(self):
        runs = self.getRuns()
        laps = dict((lap.index, lap) for [lap] in self.getLaps())
        tracks = dict(
            (track_points[0].index, track_points)
            for track_points in self.getTracks())
        activities = []
        for [run] in runs:
            if run.track_index == INVALID_TRACK:
                # We don't have any tracks for this run.
                continue
            activity = Activity(run.sport_type)
            activity.track = tracks[run.track_index]
            for lap_index in range(run.first_lap_index, run.last_lap_index+1):
                lap = laps[lap_index]
                activity.laps.append(lap)
            activities.append(activity)
        return activities

    def export_activities(self, directory):
        """Export all activites into separate files in :directory:."""
        if not os.path.exists(directory):
            os.mkdir(directory)
        print "Getting data from GPS (this might take a while)..."
        gps_name, rest = self.prod_descs[0].split(' ', 1)
        gps_info = GPSInfo(gps_name, self.soft_ver, self.prod_id, self.unit_id)
        for activity in self.get_activities():
            export = ActivityTCXExport(activity, gps_info)
            export_path = os.path.join(directory, export.filename + '.tcx')
            if not os.path.exists(export_path):
                print "Exporting to %s" % export_path
                export.export_to(export_path)


class GarminSync:
    """Main application class."""

    def __init__(self, args):
        parser = OptionParser()
        parser.add_option(
            "-d", "--debug", dest="debug",
            help="what types of debug info to show. (all,usb)",
            metavar="DEBUG_TYPE", default='')
        self.options, self.args = parser.parse_args(args)

    def setUpLogging(self, debug):
        """Set up the logging handlers."""
        debug_loggers = [debug_log.strip() for debug_log in debug.split(',')]
        console = logging.StreamHandler()
        if 'all' in debug_loggers:
            # 'all' includes all logging handlers. Only need to set up
            # the root logger.
            loggers = [logging.getLogger('')]
        else:
            loggers = [
                logging.getLogger('pygarmin.%s' % debug_log)
                for debug_log in debug_loggers]
        for logger in loggers:
            logger.addHandler(console)
            logger.setLevel(logging.DEBUG)

    def run(self):
        self.setUpLogging(self.options.debug)
        link = garmin.USBLink()
        gps = ActivityGarmin(link)
        gps.export_activities('/home/perry/data/garmin')
        return 0
