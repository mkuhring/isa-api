"""Tests on serializing planning objects in isatools.create.models to JSON"""
import json
import os
import unittest
from io import StringIO

from isatools.create.models import *
from isatools.tests import utils


def ordered(o):  # to enable comparison of JSONs with lists using ==
    if isinstance(o, dict):
        return sorted((k, ordered(v)) for k, v in o.items())
    if isinstance(o, list):
        return sorted(ordered(x) for x in o)
    else:
        return o


class EncodeToJsonTests(unittest.TestCase):

    def setUp(self):
        self.plan = SampleAssayPlan()
        self.plan.group_size = 20
        self.plan.add_sample_type('liver')
        self.plan.add_sample_type('tissue')
        self.plan.add_sample_plan_record('liver', 3)
        self.plan.add_sample_plan_record('tissue', 5)

        self.top_mods = DNAMicroAssayTopologyModifiers()
        self.top_mods.technical_replicates = 2
        self.top_mods.array_designs = {'A-AFFY-27', 'A-AFFY-28'}

        self.assay_type = AssayType(measurement_type='genome sequencing',
                                    technology_type='DNA microarray')

        factory = TreatmentFactory(intervention_type=INTERVENTIONS['CHEMICAL'],
                                   factors=BASE_FACTORS)
        factory.add_factor_value(BASE_FACTORS[0], 'calpol')
        factory.add_factor_value(BASE_FACTORS[0], 'no agent')
        factory.add_factor_value(BASE_FACTORS[1], 'low')
        factory.add_factor_value(BASE_FACTORS[1], 'high')
        factory.add_factor_value(BASE_FACTORS[2], 'short')
        factory.add_factor_value(BASE_FACTORS[2], 'long')
        self.treatment_sequence = TreatmentSequence(
            ranked_treatments=factory.compute_full_factorial_design())

    def test_serialize_dna_micro_assay_default_topology_modifiers(self):
        expected = ordered(
            json.loads("""{
                "technical_replicates": 1,
                "array_designs": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(DNAMicroAssayTopologyModifiers(),
                           cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_dna_seq_assay_default_topology_modifiers(self):
        expected = ordered(
            json.loads("""{
                "technical_replicates": 1,
                "distinct_libraries": 0,
                "instruments": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(DNASeqAssayTopologyModifiers(),
                           cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_ms_assay_default_topology_modifiers(self):
        expected = ordered(
            json.loads("""{
                "technical_replicates": 1,
                "instruments": [],
                "injection_modes": [],
                "chromatography_instruments": [],
                "acquisition_modes": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(MSAssayTopologyModifiers(),
                           cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_nmr_assay_default_topology_modifiers(self):
        expected = ordered(
            json.loads("""{
                "technical_replicates": 1,
                "instruments": [],
                "injection_modes": [],
                "pulse_sequences": [],
                "acquisition_modes": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(NMRAssayTopologyModifiers(),
                           cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_default_assay_type(self):
        expected = ordered(
            json.loads("""{
                "measurement_type": "",
                "technology_type": "",
                "topology_modifiers": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(AssayType(), cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_assay_type(self):
        expected = ordered(
            json.loads("""{
                "measurement_type": "genome sequencing",
                "technology_type": "DNA microarray",
                "topology_modifiers": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(self.assay_type, cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_assay_type_with_dna_micro_top_mods(self):
        self.assay_type.topology_modifiers = self.top_mods

        expected = ordered(
            json.loads("""{
                "topology_modifiers": {
                    "technical_replicates": 2,
                    "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                },
                "measurement_type": "genome sequencing",
                "technology_type": "DNA microarray"
            }""")
        )
        actual = ordered(
            json.loads(
                json.dumps(self.assay_type, cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_default_sampleassayplan(self):
        expected = ordered(
            json.loads("""{
                "group_size": 0,
                "assay_types": [],
                "sample_plan": [],
                "sample_types": [],
                "sample_qc_plan": [],
                "assay_plan": []
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(SampleAssayPlan(), cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_sampleplan(self):
        expected = ordered(
            json.loads("""{
                "group_size": 20,
                "assay_plan": [],
                "sample_plan": [
                    {
                        "sample_type": "liver",
                        "sampling_size": 3
                    },
                    {
                        "sample_type": "tissue",
                        "sampling_size": 5
                    }
                ],
                "sample_qc_plan": [],
                "assay_types": [],
                "sample_types": ["liver", "tissue"]
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(self.plan, cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_sampleplan_with_qc(self):
        self.plan.add_sample_type('water')
        self.plan.add_sample_qc_plan_record('water', 8)

        expected = ordered(
            json.loads("""{
                        "group_size": 20,
                        "assay_plan": [],
                        "sample_plan": [
                            {
                                "sample_type": "liver",
                                "sampling_size": 3
                            },
                            {
                                "sample_type": "tissue",
                                "sampling_size": 5
                            }
                        ],
                        "sample_qc_plan": [
                            {
                                "sample_type": "water",
                                "injection_interval": 8
                            }
                        ],
                        "assay_types": [],
                        "sample_types": ["liver", "tissue", "water"]
                    }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(self.plan, cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_sampleassayplan(self):
        self.plan.add_sample_type('water')
        self.plan.add_sample_qc_plan_record('water', 8)

        self.assay_type.topology_modifiers = self.top_mods

        self.plan.add_assay_type(self.assay_type)
        self.plan.add_assay_plan_record('liver', self.assay_type)
        self.plan.add_assay_plan_record('tissue', self.assay_type)

        expected = ordered(
            json.loads("""{
                "sample_types": ["liver", "tissue", "water"],
                "group_size": 20,
                "sample_plan": [
                    {
                        "sampling_size": 3,
                        "sample_type": "liver"
                    },
                    {
                        "sampling_size": 5,
                        "sample_type": "tissue"
                    }
                ],
                "sample_qc_plan": [
                    {
                        "injection_interval": 8,
                        "sample_type": "water"
                    }
                ],
                "assay_types": [
                    {
                        "topology_modifiers": {
                            "technical_replicates": 2,
                            "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                        }, 
                        "technology_type": "DNA microarray", 
                        "measurement_type": "genome sequencing"
                    }],
                "assay_plan": [
                    {
                        "sample_type": "liver",
                        "assay_type": {
                            "topology_modifiers": {
                                "technical_replicates": 2,
                                "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                            },
                            "technology_type": "DNA microarray",
                            "measurement_type": "genome sequencing"
                        }
                    },
                    {
                        "sample_type": "tissue",
                        "assay_type": {
                            "topology_modifiers": {
                                "technical_replicates": 2,
                                "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                            }, 
                            "technology_type": "DNA microarray", 
                            "measurement_type": "genome sequencing"
                        }
                    }
                ]
            }""")
        )

        actual = ordered(
            json.loads(
                json.dumps(self.plan, cls=SampleAssayPlanEncoder)
            )
        )
        self.assertTrue(expected == actual)

    def test_serialize_treatment_sequence(self):

        expected = ordered(json.loads("""{
            "rankedTreatments": [
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": "",
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                }
            ]
        }"""))

        actual = ordered(
            json.loads(
                json.dumps(self.treatment_sequence, cls=TreatmentSequenceEncoder)
            )
        )
        self.assertTrue(expected == actual)


class DecodeFromJsonTests(unittest.TestCase):

    def setUp(self):
        self.plan = SampleAssayPlan()
        self.plan.group_size = 20
        self.plan.add_sample_type('liver')
        self.plan.add_sample_type('tissue')
        self.plan.add_sample_plan_record('liver', 3)
        self.plan.add_sample_plan_record('tissue', 5)

        self.top_mods = DNAMicroAssayTopologyModifiers()
        self.top_mods.technical_replicates = 2
        self.top_mods.array_designs = {'A-AFFY-27', 'A-AFFY-28'}

        self.assay_type = AssayType(measurement_type='genome sequencing',
                                    technology_type='DNA microarray')

        factory = TreatmentFactory(intervention_type=INTERVENTIONS['CHEMICAL'],
                                   factors=BASE_FACTORS)
        factory.add_factor_value(BASE_FACTORS[0], 'calpol')
        factory.add_factor_value(BASE_FACTORS[0], 'no agent')
        factory.add_factor_value(BASE_FACTORS[1], 'low')
        factory.add_factor_value(BASE_FACTORS[1], 'high')
        factory.add_factor_value(BASE_FACTORS[2], 'short')
        factory.add_factor_value(BASE_FACTORS[2], 'long')
        self.treatment_sequence = TreatmentSequence(
            ranked_treatments=factory.compute_full_factorial_design())

    def test_decode_sample_assay_plan(self):
        decoder = SampleAssayPlanDecoder()
        sample_assay_plan = decoder.load(StringIO("""{
                "sample_types": ["liver", "tissue", "water"],
                "group_size": 20,
                "sample_plan": [
                    {
                        "sampling_size": 3,
                        "sample_type": "liver"
                    },
                    {
                        "sampling_size": 5,
                        "sample_type": "tissue"
                    }
                ],
                "sample_qc_plan": [
                    {
                        "injection_interval": 8,
                        "sample_type": "water"
                    }
                ],
                "assay_types": [
                    {
                        "topology_modifiers": {
                            "technical_replicates": 2,
                            "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                        }, 
                        "technology_type": "DNA microarray", 
                        "measurement_type": "genome sequencing"
                    }],
                "assay_plan": [
                    {
                        "sample_type": "liver",
                        "assay_type": {
                            "topology_modifiers": {
                                "technical_replicates": 2,
                                "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                            },
                            "technology_type": "DNA microarray",
                            "measurement_type": "genome sequencing"
                        }
                    },
                    {
                        "sample_type": "tissue",
                        "assay_type": {
                            "topology_modifiers": {
                                "technical_replicates": 2,
                                "array_designs": ["A-AFFY-27", "A-AFFY-28"]
                            }, 
                            "technology_type": "DNA microarray", 
                            "measurement_type": "genome sequencing"
                        }
                    }
                ]
            }"""))

        self.plan.add_sample_type('water')
        self.plan.add_sample_qc_plan_record('water', 8)

        self.assay_type.topology_modifiers = self.top_mods

        self.plan.add_assay_type(self.assay_type)
        self.plan.add_assay_plan_record('liver', self.assay_type)
        self.plan.add_assay_plan_record('tissue', self.assay_type)

        self.assertEqual(sample_assay_plan, self.plan)

    def test_IsaModelFactory_NMR_serialization_issue_293(self):
        decoder = SampleAssayPlanDecoder()
        sample_assay_plan = decoder.load(StringIO("""{
                "sample_types": ["liver", "tissue", "water"],
                "group_size": 20,
                "sample_plan": [
                    {
                        "sampling_size": 3,
                        "sample_type": "liver"
                    },
                    {
                        "sampling_size": 5,
                        "sample_type": "tissue"
                    }
                ],
                "sample_qc_plan": [
                    {
                        "injection_interval": 8,
                        "sample_type": "water"
                    }
                ],
                "assay_types": [
                    {
                        "topology_modifiers": {
                            "technical_replicates": 2,
                            "injection_modes": [],
                            "instruments": ["Instrument A"],
                            "pulse_sequences": ["TOCSY"],
                            "acquisition_modes": ["mode1"]
                        }, 
                        "technology_type": "nmr spectroscopy",
                        "measurement_type": "metabolite profiling"
                    }],
                "assay_plan": [
                    {
                        "sample_type": "liver",
                        "assay_type": {
                            "topology_modifiers": {
                                "technical_replicates": 2,
                                "injection_modes": [],
                                "instruments": ["Instrument A"],
                                "pulse_sequences": ["TOCSY"],
                                "acquisition_modes": ["mode1"]
                            },
                            "technology_type": "nmr spectroscopy",
                            "measurement_type": "metabolite profiling"
                        }
                    },
                    {
                        "sample_type": "tissue",
                        "assay_type": {
                            "topology_modifiers": {
                                "technical_replicates": 2,
                                "injection_modes": [],
                                "instruments": ["Instrument A"],
                                "pulse_sequences": ["TOCSY"],
                                "acquisition_modes": ["mode1"]
                            }, 
                            "technology_type": "nmr spectroscopy", 
                            "measurement_type": "metabolite profiling"
                        }
                    }
                ]
            }"""))

        with open(os.path.join(utils.JSON_DATA_DIR, 'create',
                               'treatment_sequence_test.json')) as json_fp:
            treatment_plan = TreatmentSequenceDecoder().load(json_fp)
        isa_object_factory = IsaModelObjectFactory(
            sample_assay_plan, treatment_plan)
        study = isa_object_factory.create_assays_from_plan()
        self.assertEqual(len(study.assays), 2)

    def test_create_from_decoded_json(self):
        with open(os.path.join(
                utils.JSON_DATA_DIR, 'create', 'sampleassayplan_test.json')) \
                as json_fp:
            sample_assay_plan = SampleAssayPlanDecoder().load(json_fp)
        with open(
                os.path.join(utils.JSON_DATA_DIR, 'create',
                             'treatment_sequence_test.json')) as json_fp:
            treatment_plan = TreatmentSequenceDecoder().load(json_fp)
        isa_object_factory = IsaModelObjectFactory(
            sample_assay_plan, treatment_plan)
        study = isa_object_factory.create_assays_from_plan()
        self.assertEqual(len(study.sources), 80)
        self.assertEqual(len(study.samples), 360)
        self.assertEqual(len(study.process_sequence), 360)

    def test_decode_treatment_sequence(self):
        decoder = TreatmentSequenceDecoder()
        treatment_sequence = decoder.load(StringIO("""{
            "rankedTreatments": [
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "calpol"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "low"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "short"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                },
                {
                    "treatment": {
                        "factorValues": [
                            {
                                "category": {
                                    "factorName": "AGENT",
                                    "factorType": {
                                        "annotationValue": "perturbation agent",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "no agent"
                            },
                            {
                                "category": {
                                    "factorName": "DURATION",
                                    "factorType": {
                                        "annotationValue": "time",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "long"
                            },
                            {
                                "category": {
                                    "factorName": "INTENSITY",
                                    "factorType": {
                                        "annotationValue": "intensity",
                                        "termSource": null,
                                        "termAccession": ""
                                    }
                                },
                                "value": "high"
                            }
                        ],
                        "treatmentType": "chemical intervention"
                    },
                    "rank": 1
                }
            ]
        }"""))

        self.assertEqual(
            repr(treatment_sequence), repr(self.treatment_sequence))

    def test_summary_from_treatment_sequence(self):
        decoder = TreatmentSequenceDecoder()
        treatment_sequence = decoder.load(StringIO("""{
                    "rankedTreatments": [
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "calpol"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "long"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "high"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "calpol"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "short"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "low"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "no agent"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "long"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "low"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "calpol"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "short"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "high"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "calpol"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "long"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "low"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "no agent"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "short"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "low"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "no agent"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "short"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "high"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        },
                        {
                            "treatment": {
                                "factorValues": [
                                    {
                                        "category": {
                                            "factorName": "AGENT",
                                            "factorType": {
                                                "annotationValue": "perturbation agent",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "no agent"
                                    },
                                    {
                                        "category": {
                                            "factorName": "DURATION",
                                            "factorType": {
                                                "annotationValue": "time",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "long"
                                    },
                                    {
                                        "category": {
                                            "factorName": "INTENSITY",
                                            "factorType": {
                                                "annotationValue": "intensity",
                                                "termSource": null,
                                                "termAccession": ""
                                            }
                                        },
                                        "value": "high"
                                    }
                                ],
                                "treatmentType": "chemical intervention"
                            },
                            "rank": 1
                        }
                    ]
                }"""))
        report = make_summary_from_treatment_sequence(treatment_sequence)
        expected_report = """{
    "number_of_treatment": 8,
    "number_of_factors": 3,
    "length_of_treatment_sequence": 1,
    "number_of_treatments": 8,
    "full_factorial": true,
    "list_of_treatments": [
        [
            {
                "factor": "INTENSITY",
                "value": "high"
            },
            {
                "factor": "AGENT",
                "value": "no agent"
            },
            {
                "factor": "DURATION",
                "value": "short"
            }
        ],
        [
            {
                "factor": "AGENT",
                "value": "no agent"
            },
            {
                "factor": "INTENSITY",
                "value": "low"
            },
            {
                "factor": "DURATION",
                "value": "short"
            }
        ],
        [
            {
                "factor": "AGENT",
                "value": "no agent"
            },
            {
                "factor": "INTENSITY",
                "value": "low"
            },
            {
                "factor": "DURATION",
                "value": "long"
            }
        ],
        [
            {
                "factor": "AGENT",
                "value": "calpol"
            },
            {
                "factor": "INTENSITY",
                "value": "low"
            },
            {
                "factor": "DURATION",
                "value": "short"
            }
        ],
        [
            {
                "factor": "AGENT",
                "value": "calpol"
            },
            {
                "factor": "INTENSITY",
                "value": "high"
            },
            {
                "factor": "DURATION",
                "value": "short"
            }
        ],
        [
            {
                "factor": "AGENT",
                "value": "calpol"
            },
            {
                "factor": "INTENSITY",
                "value": "low"
            },
            {
                "factor": "DURATION",
                "value": "long"
            }
        ],
        [
            {
                "factor": "INTENSITY",
                "value": "high"
            },
            {
                "factor": "AGENT",
                "value": "no agent"
            },
            {
                "factor": "DURATION",
                "value": "long"
            }
        ],
        [
            {
                "factor": "AGENT",
                "value": "calpol"
            },
            {
                "factor": "INTENSITY",
                "value": "high"
            },
            {
                "factor": "DURATION",
                "value": "long"
            }
        ]
    ],
    "number_of_factor_levels_per_factor": {
        "AGENT": [
            "calpol",
            "no agent"
        ],
        "INTENSITY": [
            "high",
            "low"
        ],
        "DURATION": [
            "short",
            "long"
        ]
    }
}"""
        self.assertEqual(sorted(json.loads(expected_report)), sorted(report))