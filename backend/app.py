#! /usr/bin/env python3

import falcon

from .cta import BusResource


def create_app():
    api = falcon.API()
    api.req_options.keep_blank_qs_values = True

    api.add_route('/stops/{stop_id}', BusResource())
    return api
