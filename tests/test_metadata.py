# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 18:08:40 2020

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import unittest
import numpy as np
import pandas as pd
from mth5 import metadata

# =============================================================================
# Tests
# =============================================================================

class TestSurveyMetadata(unittest.TestCase):
    """
    test metadata in is metadata out
    """
    def setUp(self):
        self.meta_dict = {'name_s': 'name test',
                          'id_s': 'id test',
                          'net_code_s': 'net_code test',
                          'start_date_s': '2019-01-02',
                          'end_date_s': '2019-03-05',
                          'northwest_corner/latitude_d': 40.09,
                          'northwest_corner/longitude_d': -115.6,
                          'southeast_corner/latitude_d': 35.90,
                          'southeast_corner/longitude_d': -118.9,
                          'datum_s': 'WGS84',
                          'location_s': 'location test',
                          'country_s': 'country test',
                          'summary_s': 'summary test',
                          'notes_s': 'notes test',
                          'acquired_by/author_s': 'author test',
                          'acquired_by/organization_s': 'organization test',
                          'acquired_by/email_s': 'email@test.mt',
                          'acquired_by/url_s': 'https:test.com',
                          'release_status_s': 'free',
                          'conditions_of_use_s': 'freedom',
                          'citation_dataset/doi_s': 'https:doi/adfa12',
                          'citation_journal/doi_s': None} 
    
        self.survey_object = metadata.Survey()
    
    def test_in_out(self):
        self.survey_object.from_dict(self.meta_dict)
        
        out_dict = self.survey_object.to_dict()
        
        self.assertEqual(self.meta_dict, out_dict)
        
class TestStationMetadata(unittest.TestCase):
    """
    test station metadata
    """
    
    def setUp(self):
        self.station_object = metadata.Station()
        self.meta_dict = {'sta_code_s': 'test sta_code',
                          'name_s': 'test name',
                          'latitude_d': 40.019,
                          'longitude_d': -117.89,
                          'elevation_d': 1230,
                          'notes_s': 'notes test',
                          'datum_s': 'data test',
                          'start_s': '2010-01-01T12:30:20.0000 UTC',
                          'end_s': '2010-01-04T07:40:30.0000 UTC',
                          'num_channels_i': 1,
                          'channels_recorded_s': 5,
                          'data_type_s': 'MT',
                          'declination/value_d': -12.3,
                          'declination/units_s': 'degrees',
                          'declination/epoch_s': 'MTM01',
                          'declination/model_s': 'MTM01',
                          'station_orientation_s': 'geographic north',
                          'orientation_method_s': 'compass',
                          'acquired_by/author_s': 'acquired test',
                          'acquired_by/email_s': 'acquired email',
                          'provenance/creation_time_s': '2010-04-01T10:10:10.0000 UTC',
                          'provenance/software/name_s': 'mth5',
                          'provenance/software/version_s': '1.0.1',
                          'provenance/software/author_s': 'Peacock',
                          'provenance/submitter/author_s': 'submitter name',
                          'provenance/submitter/organization_s': 'mt inc',
                          'provenance/submitter/url_s': 'mt.edi',
                          'provenance/submitter/email_s': 'mt@em.edi',
                          'provenance/notes_s': 'goats',
                          'provenance/log_s': 'EY flipped'}
              
        
    def test_in_out(self):
        self.station_object.from_dict(self.meta_dict)
        out_dict = self.station_object.to_dict()
        self.assertEqual(self.meta_dict, out_dict)
        
# =============================================================================
# run
# =============================================================================
if __name__ == '__main__':
    unittest.main()