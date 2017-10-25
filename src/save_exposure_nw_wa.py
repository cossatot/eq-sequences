# LICENSE
#
# Copyright (c) 2017, GEM Foundation, Anirudh Rao
#
# The build_exposure script is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>
#
# DISCLAIMER
#
# The software provided herein is released as a prototype implementation on
# behalf of scientists and engineers working within the GEM Foundation
# (Global Earthquake Model).
#
# It is distributed for the purpose of open collaboration and in the
# hope that it will be useful to the scientific, engineering, disaster
# risk and software design INDmunities.
#
# This software is NOT distributed as part of GEM's OpenQuake suite
# (http://www.globalquakemodel.org/openquake) and must be considered as a
# separate entity. The software provided herein is designed and implemented
# by scientific staff. It is not developed to the design standards, nor
# subject to same level of critical review by professional software
# developers, as GEM's OpenQuake software suite.
#
# Feedback and contribution to the software is welINDe, and can be
# directed to the risk scientific staff of the GEM Model Facility
# (risk@globalquakemodel.org).
#
# The software herein is therefore distributed WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# The GEM Foundation, and the authors of the software, assume no
# liability for use of the software.

"""
Convert exposure model csv files to xml.
"""

import collections
import csv
from lxml import etree
import pandas as pd
from tqdm import tqdm

NAMESPACE = 'http://openquake.org/xmlns/nrml/0.5'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}

exposure_csv_dir = "/Users/anirudh/GEM/Projects/USA/data/processed/exposure/hazus-based/RES/"
exposure_xml_dir = "./"

exposure_csv_file = exposure_csv_dir + "washington.csv"

Metadata = collections.namedtuple(
    "Metadata",
    ["exposure_category", "taxonomy_source", "area_type", "area_unit",
     "cost_structural_aggregation_type", "cost_structural_currency",
     "cost_contents_aggregation_type", "cost_contents_currency"])

metadata = Metadata(
    exposure_category="buildings",
    taxonomy_source="HAZUS",
    area_type="aggregated",
    area_unit="SQFT",
    cost_structural_aggregation_type="aggregated",
    cost_structural_currency="USD",
    cost_contents_aggregation_type="aggregated",
    cost_contents_currency="USD")

nw_wa_tracts_file = "puget_sound_hazard_risk/data/nw_washington_tracts.csv"
nw_wa_tracts_df = pd.read_csv(nw_wa_tracts_file)
nw_wa_tracts = nw_wa_tracts_df["GEOID"].values.tolist()

filter_tracts = nw_wa_tracts

def write_exposure_locations(location_file, data, filter_tracts):
    with open(location_file, "w") as csvfile:
        f = csv.writer(csvfile)
        for row_index, row in tqdm(data.iterrows(), total=data.shape[0]):
            tract = int(row['asset'][0:11])
            if tract not in filter_tracts:
                continue
            f.writerow([row['lon'], row['lat']])


def write_exposure_xml(xml_file, model_id, model_desc, metadata, data, filter_tracts):
    with open(xml_file, "wb") as f:
        root = etree.Element('nrml', nsmap=SERIALIZE_NS_MAP)
        node_em = etree.SubElement(root, "exposureModel")
        node_em.set("id", model_id)
        node_em.set("category", metadata.exposure_category)
        node_em.set("taxonomySource", metadata.taxonomy_source)

        node_desc = etree.SubElement(node_em, "description")
        node_desc.text = model_desc

        node_conv = etree.SubElement(node_em, "conversions")

        node_area = etree.SubElement(node_conv, "area")
        node_area.set("type", metadata.area_type)
        node_area.set("unit", metadata.area_unit)

        node_cost_types = etree.SubElement(node_conv, "costTypes")

        node_cost_type_s = etree.SubElement(node_cost_types, "costType")
        node_cost_type_s.set("name", "structural")
        node_cost_type_s.set("type", metadata.cost_structural_aggregation_type)
        node_cost_type_s.set("unit", metadata.cost_structural_currency)

        node_cost_type_c = etree.SubElement(node_cost_types, "costType")
        node_cost_type_c.set("name", "contents")
        node_cost_type_c.set("type", metadata.cost_contents_aggregation_type)
        node_cost_type_c.set("unit", metadata.cost_contents_currency)

        node_assets = etree.SubElement(node_em, "assets")
        for row_index, row in tqdm(data.iterrows(), total=data.shape[0]):
            tract = int(row['asset'][0:11])
            if tract not in filter_tracts:
                continue
            if not row['number'] * row['area']:
                continue
            node_asset = etree.SubElement(node_assets, "asset")
            node_asset.set("id", str(row['asset']))
            node_asset.set("number", str(row['number']))
            node_asset.set("area", str(row['area'] * 1000))
            node_asset.set("taxonomy", str(row['taxonomy']))

            node_location = etree.SubElement(node_asset, "location")
            node_location.set("lon", str(row['lon']))
            node_location.set("lat", str(row['lat']))

            node_costs = etree.SubElement(node_asset, "costs")

            node_cost_s = etree.SubElement(node_costs, "cost")
            node_cost_s.set("type", 'structural')
            node_cost_s.set("value", str(row['structural'] * 1000))

            node_cost_c = etree.SubElement(node_costs, "cost")
            node_cost_c.set("type", 'contents')
            node_cost_c.set("value", str(row['contents'] * 1000))

        f.write(etree.tostring(root, pretty_print=True,
                               xml_declaration=True, encoding='UTF-8'))


xml_file = exposure_xml_dir + "nw-washington.xml"
model_id = "exposure-nw-washington"
model_desc = "Exposure model for North West Washington"
data = pd.io.parsers.read_csv(exposure_csv_file)
location_file = exposure_xml_dir + "nw_washington_sites.csv"
write_exposure_locations(location_file, data, filter_tracts)
write_exposure_xml(xml_file, model_id, model_desc, metadata, data, filter_tracts)
