FROM python:3.11.2

# Copy everything in project
COPY . .

# Install project dependencies
RUN pip install -r requirements.txt

ENV PYTHONPATH=.
CMD ["./startup.sh"]
