#!/usr/bin/env python3
# pylint: disable=C0301,C0111

"""
A script for rendering AWS dashboards to be viewed without logging in.
Supply AWS credentials via an assigned role in IAM or environment variables.

Usage example: ./aws-dashboard.py all > foo.html

Logger runtime output will go to stderr.
"""

import base64
import datetime
import json
import logging
import sys

import boto3
from botocore.exceptions import ClientError

__author__ = "Markus Koskinen"
__license__ = "BSD"

_LOG_FORMAT = "%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s"
_DEBUG = False

logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)

def syntax(execname):
    print("Syntax: %s [dashboard_name]" % execname)
    sys.exit(1)

def auth():
    """ TODO: This not quite how it should be done. """
    try:
        api = boto3.client('cloudwatch')
    except ClientError as e:
        logging.error("Client error: %s", e)
        exit(1)
        return e
    else:
        return api

def get_dashboard_images(dashboard_name="all", encode_base64=True):
    """ Returns a list of base64 encoded PNGs of dashboard metrics. """
    cloudwatch_api = auth()

    dashboard_list = [d['DashboardName'] for d in cloudwatch_api.list_dashboards()['DashboardEntries']]

    logging.info("Dashboards available: %s Rendering: %s", dashboard_list, dashboard_name)

    if dashboard_name != "all" and dashboard_name in dashboard_list:
        dashboard_list = [dashboard_name]

    dashboard_widget_properties = {}
    dashboard_images = {}

    logging.debug("Dashboards available: %s ", dashboard_list)

    for dashboard in dashboard_list:
        dashboard_widget_properties[dashboard] = [dp['properties'] for dp in json.loads(cloudwatch_api.get_dashboard(DashboardName=dashboard)['DashboardBody'])['widgets'] if 'metrics' in dp['properties']]
        dashboard_images[dashboard] = []

        for dashboard_widget_property in dashboard_widget_properties[dashboard]:
            #logging.debug(json.dumps(dashboard_widget_property))

            dashboard_image = cloudwatch_api.get_metric_widget_image(MetricWidget=json.dumps(dashboard_widget_property))['MetricWidgetImage']

            if encode_base64:
                dashboard_image = base64.b64encode(dashboard_image).decode('utf-8')

            dashboard_images[dashboard].append(dashboard_image)

    result = [item for sublist in dashboard_images.values() for item in sublist]
    logging.info("Result size: %d ", len(result))

    return result



def main(argv):
    """ Outputs a HTML page to stdout with inline base64 encoded PNG dashboards. """
    dashboard_name = "all"

    if len(argv) == 2:
        dashboard_name = argv[1]

    result = "<html>\n"

    start_time = datetime.datetime.now()
    result += "<!-- Generation started: " + start_time.isoformat() + " -->\n"

    for image in get_dashboard_images(dashboard_name=dashboard_name):
        result += "  <img src='data:image/png;base64," + str(image) + "' />\n"

    end_time = datetime.datetime.now()
    result += "<!-- Generation ended: " + end_time.isoformat() + " -->\n"
    result += "</html>\n"

    print("%s" % result)
    logging.info("Completed. Start time: %s Runtime: %s ", start_time, str(end_time-start_time))

    return 0

if __name__ == "__main__":
    if len(sys.argv) not in  (1, 2):
        syntax(sys.argv[0])
    sys.exit(main(sys.argv))
