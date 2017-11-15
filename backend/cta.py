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


class BusResource(object):

    @staticmethod
    def upcoming_buses(bus_schedule, curr_time):
        """Given bus schedule and current time, calculate upcoming buses
        """
        cleaned_results = []
        if bus_schedule:
            for bus in bus_schedule:
                predicted_time = maya.parse(bus['prdtm'])
                min_till_next_bus = (
                    (predicted_time.epoch - curr_time.epoch) / 60
                )

                bus_to_add = {}
                bus_to_add['bus'] = bus['rt']
                bus_to_add['min_away'] = math.floor(min_till_next_bus)
                cleaned_results.append(bus_to_add)

        return cleaned_results

    def on_get(self, req, resp, stop_id):
        """GET method for BusResource
        """

        right_now = maya.MayaDT.from_datetime(datetime.datetime.now())

        # get data from CTA Bus Tracker API
        payload = {
            'key': CTA_API_KEY,
            'stpid': stop_id,
            'format': 'json'
        }

        try:
            r = requests.get(CTA_BASE_URL, params=payload)
        except ConnectionError:
            body = {'error': 'URL not found'}
        else:
            if r.status_code == 200:
                response_type = r.json().get('bustime-response', dict())

                # response_type can be 'error'  or 'prd'
                # need to parse and send out accordingly
                if 'prd' in response_type:
                    bus_schedule = response_type.get('prd')
                    body = {
                        'result': self.upcoming_buses(bus_schedule, right_now)
                    }
                elif 'error' in response_type:
                    # TODO handle error
                    body = {}
                else:
                    # TODO unknown type. pass back JSON
                    body = {}

            else:
                body = {'error': f'Request returned {r.status_code}'}
        finally:
            resp.status_code = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.data = json.dumps(body, ensure_ascii=False).encode('utf-8')
