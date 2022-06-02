FROM docker.io/fnndsc/mni-conda-base:unofficial

LABEL org.opencontainers.image.authors="Jennings Zhang <Jennings.Zhang@childrens.harvard.edu>" \
      org.opencontainers.image.title="pl-fetal-cp-surface-extract" \
      org.opencontainers.image.description="Fetal brain MRI CP surface extraction using CIVET marching-cubes"

WORKDIR /usr/local/src/pl-fetal-cp-surface-extract

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["extract_cp", "--help"]
