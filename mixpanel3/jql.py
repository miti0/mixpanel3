import sys
import json
import logging
import http.client
import pandas as pd
import configargparse
import time
import base64
import urllib.request


class JQL:
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add("--api_secret", help="Mixpanel API secret", required=True)
    arg_parser.add("--from_date", help="Export starting date (for ex. 2018-01-01)", required=False)
    arg_parser.add("--to_date", help="Export ending date (for ex. 2018-02-01)", required=False)
    arg_parser.add("--jql_payload", help="JQL Payload query", required=False)
    request_url = 'https://mixpanel.com/api/2.0/jql/'

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def __init__(self, api_secret):
        self.api_secret = api_secret
        # self.from_date =
        self.logger = logging.getLogger(__name__)

    def run(self, jql_payload):
        """
        Functions sends request and returns result parsed as Pandas DataFrame
        Input: JQL query data in raw/text format URL encoded
        Returns pandas dataframe
        """
        start_time = int(time.time())
        b64val = base64.b64encode(self.api_secret.encode())

        # urlib implementation
        req = urllib.request.Request(self.request_url)
        req.add_header("Authorization", "Basic %s" % b64val.decode("utf-8"))
        self.logger.info("Sending jql POST request..")
        res = urllib.request.urlopen(req, str.encode(jql_payload), )
        self.logger.info("Request done. Result: " + str(res.code) + ', in (sec): '
                         + str(int(time.time()-start_time)))

        if res.code != 200:
            self.logger.error("JQL run() Received not 200 result!")
            raise ValueError("JQL run() Received not 200 result!")

        self.logger.info("Reading response..")
        res_read_time_start = time.time()
        data = res.read()
        self.logger.info("done in (sec): " + str(int(time.time() - res_read_time_start)))

        """
        # http.client implementation

        conn = http.client.HTTPSConnection("mixpanel.com")
        headers = {
            'authorization': "Basic " + b64val.decode("utf-8")
        }
        
        conn.request("POST", "/api/2.0/jql/", jql_payload, headers)

        self.logger.info("Sending jql request..")
        res = conn.getresponse()
        self.logger.info("Request done. Result: " + str(res.code) + ', in (sec): '
                         + str(int(time.time()-start_time)))

        if res.code != 200:
            self.logger.error("JQL run() Received not 200 result!")
            raise ValueError("JQL run() Received not 200 result!")

        self.logger.info("Reading response..")
        res_read_time_start = time.time()
        data = res.read()
        self.logger.info("done in (sec): " + str(int(time.time() - res_read_time_start)))
        """

        self.logger.info("Loading response to json..")
        json_res_time_start = time.time()
        json_res = json.loads(data)
        self.logger.info("done in (sec): " + str(int(time.time() - json_res_time_start)))

        self.logger.info("Loading json to pandas..")
        pandas_load_time_start = time.time()
        df = pd.DataFrame(json_res['results'])
        end_time = int(time.time())
        self.logger.info("done in (sec): " + str(int(end_time - pandas_load_time_start)))

        self.logger.info("Fetching and parsing done in (sec.): " + str(end_time-start_time))
        return df

