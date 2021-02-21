FROM python:3

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install https://github.com/oroszgy/spacy-hungarian-models/releases/download/hu_core_ud_lg-0.3.1/hu_core_ud_lg-0.3.1-py3-none-any.whl  

CMD cd /nlp && jupyter notebook NLP.ipynb --allow-root --NotebookApp.iopub_data_rate_limit=1e10