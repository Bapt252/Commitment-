#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Package services contenant les services utilisés par l'application."""

# Exposer les classes de services pour faciliter l'importation
from app.services.parser_service_interface import ParserServiceInterface
from app.services.existing_cv_parser_adapter import ExistingCVParserAdapter
from app.services.existing_job_parser_adapter import ExistingJobParserAdapter
from app.services.combined_parser_service import CombinedParserService
