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
    def _process_cta_response(resp_json, curr_time):
        """Based on CTA reaponse header, process information
        Return
            * body - response body
            * error_flag - boolean indicating if response is an error

        Field Description
            * 'prd' ~ predicted bus times
            * 'error' ~ something went wrong, parse and let user know
        """
        # TODO logging

        error_flag = True
        result = ''

        response_type = resp_json.get('bustime-response', dict())
        if 'prd' in response_type:
            error_flag = False
            bus_schedule = response_type.get('prd')
            result = BusResource._upcoming_buses(bus_schedule, curr_time)
        elif 'error' in response_type:
            error_details = response_type.get('error')[0]
            if 'stpid' in error_details:
                result = f"stop_id: {error_details['stpid']} does not exist"
            else:
                result = error_details
        else:
            # got something we didn't except
            # log it and send client a message letting them know something was off
            pass
        return result, error_flag

    @staticmethod
    def _structure_response(body, error_flag):
        if error_flag:
            resp_body = {'error': body}
        else:
            resp_body = {'result': body}
        return resp_body

    @staticmethod
    def _upcoming_buses(bus_schedule, curr_time):
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
        error_flag = True
        curr_time = maya.MayaDT.from_datetime(datetime.datetime.now())

        # get data from CTA Bus Tracker API
        payload = {
            'key': CTA_API_KEY,
            'stpid': stop_id,
            'format': 'json'
        }
        try:
            r = requests.get(CTA_BASE_URL, params=payload)
        except ConnectionError:
            body = 'URL not found'
        else:
            if r.status_code == 200:
                body, error_flag = (
                    self._process_cta_response(r.json(), curr_time)
                )
            else:
                body = f'Request returned {r.status_code}'
        finally:
            resp.status_code = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp_body = self._structure_response(body, error_flag)
            resp.data = (
                json.dumps(resp_body, ensure_ascii=False)
                    .encode('utf-8')
            )
