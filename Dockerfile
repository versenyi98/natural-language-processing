FROM python:3

COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD cd /nlp && jupyter notebook NLP.ipynb --allow-root --NotebookApp.iopub_data_rate_limit=1e10