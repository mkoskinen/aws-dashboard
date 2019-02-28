# aws-dashboard

A small script for rendering a dashboard or all your dashboards from CloudWatch.

Running from cli renders to a HTML file as inline PNGs. Or you can call get_dashboard_images and work on the returned list.
This early example can be run eg via cron but a lambda version should be pretty quick to do as well.

Supply AWS credentials via an assigned role in IAM or environment variables.

Usage example: ./aws-dashboard.py all > foo.html

Logger runtime output will go to stderr.

Note:
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_widget_image

There is a limit of 20 transactions per second for this API.

Each GetMetricWidgetImage action has the following limits:

As many as 100 metrics in the graph.
Up to 100 KB uncompressed payload.