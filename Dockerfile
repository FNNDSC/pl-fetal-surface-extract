FROM docker.io/fnndsc/pl-fetal-surface-extract:base-1

LABEL org.opencontainers.image.authors="Jennings Zhang <Jennings.Zhang@childrens.harvard.edu>" \
      org.opencontainers.image.title="pl-fetal-surface-extract" \
      org.opencontainers.image.description="Fetal brain MRI surface extraction using CIVET marching-cubes"

WORKDIR /usr/local/src/pl-fetal-surface-extract

RUN conda install -c conda-forge -y numpy=1.22.3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["extract_cp", "--help"]
