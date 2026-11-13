PYTHON ?= python3
export PYTHONPATH=src
.PHONY: demo generate warehouse metrics audit dashboard test validate release pdf clean

demo:
	$(PYTHON) -m tahr.cli demo

generate:
	$(PYTHON) -m tahr.cli generate

warehouse:
	$(PYTHON) -m tahr.cli warehouse

metrics:
	$(PYTHON) -m tahr.cli metrics

audit:
	$(PYTHON) -m tahr.cli audit

validate:
	$(PYTHON) -m tahr.cli validate

test:
	$(PYTHON) -m unittest discover -s tests -v

release:
	$(PYTHON) scripts/verify_release.py

pdf:
	$(PYTHON) scripts/build_case_study_pdf.py

dashboard:
	streamlit run app/dashboard.py

clean:
	rm -f data/raw/*.csv data/restricted/*.csv data/processed/*.sqlite reports/*.json reports/*.html
