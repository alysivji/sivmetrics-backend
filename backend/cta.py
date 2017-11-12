#! /usr/bin/env python3

# standard library
import datetime
import json
import math
import os

# other libraries
import falcon
import maya
import requests

# constants
CTA_BASE_URL = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'
CTA_API_KEY = os.getenv('CTA_API_KEY', None)


class Bus(object):

    def on_get(self, req, resp, stop_id):
        right_now = maya.MayaDT.from_datetime(datetime.datetime.now())

        # get data from CTA Bus Tracker API
        payload = {
            'key': CTA_API_KEY,
            'stpid': stop_id,
            'format': 'json'
        }
        r = requests.get(CTA_BASE_URL, params=payload)

        # parse response
        upcoming_buses = r.json().get('bustime-response', None)
        if upcoming_buses:
            upcoming_buses = upcoming_buses.get('prd', None)

        cleaned_results = []
        if upcoming_buses:
            for bus in upcoming_buses:
                predicted_time = maya.parse(bus['prdtm'])
                min_till_next_bus = (
                    (predicted_time.epoch - right_now.epoch) / 60
                )

                bus_to_add = {}
                bus_to_add['bus'] = bus['rt']
                bus_to_add['min_away'] = math.floor(min_till_next_bus)
                cleaned_results.append(bus_to_add)

        resp.data = (
            json.dumps(cleaned_results, ensure_ascii=False)
                .encode('utf-8')
        )
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200
