"""
Variable constants common to this project
"""

from pathlib import Path

COLUMNS_TO_DE_IDENTIFY = ["AuthoringProviderKey",
                          "AuthorizingProviderKey",
                          "CosignProviderKey",
                          "EncounterCSN",
                          "EncounterKey",
                          "MRN_GNV",
                          "MRN_JAX",
                          "NoteID",  # ?
                          "NoteKey",  # ?
                          "OrderID",  # ?
                          "OrderKey",  # ?
                          "PatientKey",
                          "ProviderKey",
                          "preceding_visit_occurrence_id",
                          "provider_id",
                          "visit_occurrence_id"]

OMOP_PORTION_DIR_MAC = Path("data/output/convertColumns/2023-03-14 13-04-07")
OMOP_PORTION_DIR_WIN = Path("data/output/convertColumns/2023-03-14 13-04-07")
