FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies (if needed)
RUN yum update -y && yum install -y gcc-c++ make && \
    yum clean all && \
    rm -rf /var/cache/yum

# Copy function code and requirements
COPY fac_recog.py requirements.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Set the CMD to your handler
CMD [ "fac_recog.lambda_handler" ]