#!/usr/bin/env python3

"""
A script for rendering AWS dashboards to be viewed without logging in.

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_widget_image
There is a limit of 20 transactions per second for this API. Each GetMetricWidgetImage action has the following limits:

As many as 100 metrics in the graph.
Up to 100 KB uncompressed payload.

"""

import base64
import json
import pprint
import sys
import time

import boto3
from botocore.exceptions import ClientError

pp = pprint.PrettyPrinter(indent=4)

_DEBUG = False

__author__ = "Markus Koskinen"
__license__ = "BSD"

def syntax(execname):
    print("Syntax: %s" % execname)
    sys.exit(1)

def auth():
    try:
        api = boto3.client('cloudwatch')
    except ClientError as e:
        print("Client error: %s" % e)
        exit(1)
        return e
    else:
        return api

def main():
    cloudwatch_api = auth()

    dashboard_list = [d['DashboardName'] for d in cloudwatch_api.list_dashboards()['DashboardEntries']]
    dashboard_widget_properties = {}
    dashboard_images = {}

    print("<!-- Dashboards available: %s -->" % dashboard_list)

    for dashboard in dashboard_list:
        dashboard_widget_properties[dashboard] = [ dp['properties'] for dp in json.loads(cloudwatch_api.get_dashboard(DashboardName=dashboard)['DashboardBody'])['widgets'] if 'metrics' in dp['properties'] ]
        dashboard_images[dashboard] = []

        for dashboard_widget_property in dashboard_widget_properties[dashboard]:
            if _DEBUG:
                pp.pprint(json.dumps(dashboard_widget_property))

            dashboard_image_b64 = base64.b64encode( cloudwatch_api.get_metric_widget_image(MetricWidget=json.dumps(dashboard_widget_property))['MetricWidgetImage'] )
            dashboard_images[dashboard].append(dashboard_image_b64)

            if _DEBUG:
                print("get metric widget image type: %s, MetricWidgetImage: %s", type(dashboard_image_b64), dashboard_image_b64 )


    result = ""

    for dashboard in dashboard_list:
        for image in dashboard_images[dashboard]:
            result += "<img src='data:image/png;base64," + image + "' >\n"

    print("%s" % result)
    return

if __name__ == "__main__":
    if len(sys.argv) != 1:
        syntax(sys.argv[0])
    main()