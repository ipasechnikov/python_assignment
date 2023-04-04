FROM python:3.11.2

# # Install curl
# RUN apk --no-cache add curl

# Install Poetry (may take some time)
# RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 && \
#     cd /usr/local/bin && \
#     ln -s /opt/poetry/bin/poetry
# ENV PATH="$PATH:$HOME/.local/bin"

# Copy everything in project
COPY . .

# Install project dependencies
RUN pip install -r requirements.txt

ENV PYTHONPATH=.
CMD ["./startup.sh"]
